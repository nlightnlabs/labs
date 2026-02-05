import os
import boto3
from typing import Any, Dict, List, Union
from pydantic import BaseModel
import base64
import json
import io, numpy as np
import pandas as pd
import logging
from pathlib import Path
from botocore.exceptions import ClientError

import pandas as pd

logger = logging.getLogger(__name__)
JSONData = Union[Dict[str, Any], List[Any]]
ParquetData = pd.DataFrame
BinaryData = bytes
TextData = str
SupportedDataTypes = Union[JSONData, ParquetData, BinaryData, TextData]


from .. import globals
ENVIRONMENT = globals.ENVIRONMENT
IS_PRODUCTION = globals.IS_PRODUCTION
AWS_REGION = globals.AWS_REGION
AWS_PROFILE = globals.AWS_PROFILE
TENANT_NAME = globals.TENANT_NAME
DBHOST = globals.DBHOST
DBUSER = globals.DBUSER
DBPORT = globals.DBPORT
DEFAULT_DB = globals.DEFAULT_DB
S3_BUCKET = globals.S3_BUCKET
S3_ROOT_PREFIX = globals.S3_ROOT_PREFIX


def get_s3_client(profile_name: str = ""):
    """Return an S3 client for a given AWS profile."""
    
    print("Environment:", ENVIRONMENT)
    
    if ENVIRONMENT == "production":
        session = boto3.Session()
    else:
        session = boto3.Session(profile_name=profile_name)
    return session.client("s3")


# Initialize the S3 client
s3_client = get_s3_client(
    profile_name=AWS_PROFILE
)


class S3PrefixModel(BaseModel):
    bucket_name: str = S3_BUCKET
    prefix: str = S3_ROOT_PREFIX
    keys: List[str] = []
    data: List[dict] = []
    upload_file_local_paths: List[str] = ["./"]
    scope: str = None


class S3KeyModel(BaseModel):
    bucket_name: str = S3_BUCKET
    keys: List[str] = []
    data: List[dict] = []
    download_directory: str = "./downloads"
    scope: str = None

async def list_folders(request: S3PrefixModel) -> List[str]:
    """
    List all 'folders' (common prefixes) in an S3 bucket under a given prefix.
    """
    print("🔍 Listing folders...")
    bucket_name = request.bucket_name
    prefix = request.prefix

    print("Bucket:", bucket_name, "Prefix:", prefix)
    
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        result = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/"):
            result.extend([cp["Prefix"] for cp in page.get("CommonPrefixes", [])])
        return result
    except Exception as e:
        print(f"❌ Error listing folders: {e}")
        return []



async def list_files(request: S3PrefixModel) -> List[Dict[str, str]]:
    """
    List all files in a given folder/prefix in an S3 bucket,
    returning file name, size (in bytes), key, and file type (extension).
    """

    print("🔍 Listing files...")
    bucket_name = request.bucket_name
    prefix = request.prefix
    
    print("Bucket:", bucket_name, "Prefix:", prefix)
    
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        file_list = []

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                size = obj["Size"]
                filename = os.path.basename(key)
                extension = os.path.splitext(filename)[1].lstrip(".").lower() or "unknown"

                file_list.append({
                    "file_name": filename,
                    "size_bytes": size,
                    "key": key,
                    "file_type": extension
                })

        return file_list

    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []


async def fetch_files(request: S3KeyModel) -> List[Dict[str, Any]]:
    """
    Fetch several files from an S3 bucket and return metadata + content
    (auto-detects binary vs text; returns base64 for binary files).

    Returns:
        List of dictionaries containing:
          - file_name
          - key
          - size_bytes
          - file_type
          - metadata (from S3)
          - content (str or base64 string)
    """
    print("📥 Fetching files from S3...")

    keys = request.keys
    bucket_name = request.bucket_name

    fetched_files = []

    for key in keys:
        try:
            # Fetch object metadata + content
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            body = response["Body"].read()
            meta = response.get("Metadata", {})

            file_name = os.path.basename(key)
            extension = os.path.splitext(file_name)[1].lstrip(".").lower() or "unknown"
            size = response["ContentLength"]

            # ✅ Determine whether the file is text or binary
            text_file_types = {"txt", "csv", "json", "xml", "log", "html"}
            if extension in text_file_types:
                try:
                    content_str = body.decode("utf-8")
                except UnicodeDecodeError:
                    # fallback to base64 if not UTF-8 compatible
                    content_str = base64.b64encode(body).decode("utf-8")
            else:
                # Binary file: convert to base64 for JSON safety
                content_str = base64.b64encode(body).decode("utf-8")

            fetched_files.append({
                "file_name": file_name,
                "key": key,
                "size_bytes": size,
                "file_type": extension,
                "metadata": meta,
                "content": content_str
            })

            print(f"✅ Fetched {file_name} ({size} bytes)")

        except Exception as e:
            print(f"❌ Error fetching {key}: {e}")

    return fetched_files


async def download_files(request: S3KeyModel) -> None:
    """
    Download several files from an S3 bucket.
    Creates the local_dir if it doesn't exist.
    """

    bucket_name = request.bucket_name
    keys = request.keys
    download_directory = request.download_directory

    os.makedirs(download_directory, exist_ok=True)
    for key in keys:
        local_path = os.path.join(download_directory, os.path.basename(key))
        try:
            print(f"⬇️  Downloading {key} -> {local_path}")
            s3_client.download_file(bucket_name, key, local_path)
        except Exception as e:
            print(f"❌ Error downloading {key}: {e}")



async def upload_files(request: S3PrefixModel) -> Dict:
    """
    Upload several local files to an S3 bucket.
    The destination key is dest_prefix + filename.
    """
    bucket_name = request.bucket_name
    prefix = request.prefix
    upload_file_local_paths = request.upload_file_local_paths 
    
    uploaded_files = []
    for local_file_path in upload_file_local_paths:
        
        filename = os.path.basename(local_file_path)

        try:
            print(f"⬆️  Uploading {local_file_path} -> s3://{bucket_name}/{filename}")
            s3_key = f"{prefix}/{filename}"
            uploaded_files.append(filename)
            s3_client.upload_file(local_file_path, bucket_name, s3_key)

        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")

    uploadCheck = S3PrefixModel(bucket_name=bucket_name, prefix=prefix)

    all_keys_in_prefix = await list_files(uploadCheck)

    files_in_prefix = [key.get("file_name") for key in all_keys_in_prefix]
    print(files_in_prefix)

    successful_uploads = []
    for file in uploaded_files:
        if file in files_in_prefix:
            successful_uploads.append(file)
    
    status = "success"
    if len(successful_uploads) < len(upload_file_local_paths):
        status = "fail"
    
    return {
            "status": status, 
            "number_of_files_uploaded":f"{len(successful_uploads)} out of {len(upload_file_local_paths)}",
            "files_uploaded": successful_uploads,
            }


async def save_json_data_file(request: S3KeyModel):

    try:
        bucket_name = request.bucket_name
        keys = request.keys
        name = keys[0]
        key = f"{name}.json"

        data = request.data

        print(bucket_name)
        print(keys)
        print(name)
        print(key)

        record_count = len(data)

        # Convert to formatted JSON bytes
        json_bytes = json.dumps(data, indent=2).encode("utf-8")

        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json_bytes,
            ContentType="application/json"
        )

        return {
            "status": "success",
            "bucket": bucket_name,
            "key": key,
            "message": f"Uploaded {record_count} records to S3"
        }

    except Exception as e:
        print(f"ERROR\n: {e}")
        raise {"status_code":500, "detail":str(e)}


async def delete_files(request: S3KeyModel) -> None:
    """
    Delete several files from an S3 bucket.
    """
    keys = request.keys
    bucket_name = request.bucket_name
    
    if not keys:
        print("⚠️  No keys provided for deletion.")
        return

    try:
        delete_objects = [{"Key": k} for k in keys]
        response = s3_client.delete_objects(
            Bucket=bucket_name, Delete={"Objects": delete_objects}
        )
        deleted = response.get("Deleted", [])
        errors = response.get("Errors", [])
        print(f"Deleted {len(deleted)} files from {bucket_name}")
        if errors:
            print(f"⚠️  Errors deleting some files: {errors}")
        return {"status": "success", "message":f"Deleted {len(deleted)} files from {bucket_name}"}
    except Exception as e:
        print(f"❌ Error deleting files: {e}")


class S3DataQuery:
    bucket_name:str = S3_BUCKET
    key:str = ""

async def get_from_s3(request: S3DataQuery) -> SupportedDataTypes:
    
    bucket_name = request.bucket_name
    key = request.key

    try:
        resp = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = resp["Body"].read()
        ext = Path(key).suffix.lower()

        if ext == ".json":
            return json.loads(content.decode("utf-8"))

        if ext in [".parquet", ".pq"]:
            import io
            return pd.read_parquet(io.BytesIO(content))

        if ext in [".csv"]:
            import io
            return pd.read_csv(io.BytesIO(content))

        if ext in [".txt", ".log", ".md", ".py", ".js", ".html", ".css"]:
            return content.decode("utf-8")

        # common binary
        if ext in [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
            ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
            ".mp3", ".wav", ".flac", ".aac",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".zip", ".tar", ".gz", ".rar",
        ]:
            return content

        # fallback: try text, else binary
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchKey":
            raise FileNotFoundError(f"{key} not found in bucket {bucket_name}")
        if code == "NoSuchBucket":
            raise FileNotFoundError(f"Bucket {bucket_name} not found")
        raise


from datetime import datetime
class SaveDataInS3Model:
    bucket_name: str = S3_BUCKET
    prefix: str = ""
    file_name: str = f"file_{datetime.now()}.txt"
    data: SupportedDataTypes = []


async def save_data_in_s3(request: SaveDataInS3Model) -> None:

    bucket_name = request.bucket_name
    prefix = request.prefix
    file_name = request.file_name
    data = request.data 

    key = f"{prefix}/{file_name}"

    try:
        ext = Path(key).suffix.lower()

        if ext == ".json":
            if not isinstance(data, (dict, list)):
                raise ValueError(f"Cannot export {type(data)} to JSON")
            body = json.dumps(data, indent=2, default=str).encode("utf-8")
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, ContentType="application/json")
            return

        if ext in [".parquet", ".pq"]:
            if not isinstance(data, pd.DataFrame):
                raise ValueError(f"Cannot export {type(data)} to Parquet")
            import io
            buf = io.BytesIO()
            data.to_parquet(buf, index=False)
            buf.seek(0)
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=buf.getvalue(), ContentType="application/octet-stream")
            return

        if ext == ".csv":
            if not isinstance(data, pd.DataFrame):
                raise ValueError(f"Cannot export {type(data)} to CSV")
            import io
            buf = io.BytesIO()
            data.to_csv(buf, index=False)
            buf.seek(0)
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=buf.getvalue(), ContentType="text/csv")
            return

        if ext in [".txt", ".log", ".md", ".py", ".js", ".html", ".css"]:
            if not isinstance(data, str):
                raise ValueError(f"Cannot export {type(data)} to text")
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data.encode("utf-8"), ContentType="text/plain")
            return

        # common binary
        if ext in [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
            ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
            ".mp3", ".wav", ".flac", ".aac",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".zip", ".tar", ".gz", ".rar",
        ]:
            if not isinstance(data, (bytes, bytearray)):
                raise ValueError(f"Cannot export {type(data)} to binary")
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data, ContentType="application/octet-stream")
            return

        # unknown extension: try text, else binary, else JSON dump
        if isinstance(data, str):
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data.encode("utf-8"), ContentType="text/plain")
        elif isinstance(data, (bytes, bytearray)):
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data, ContentType="application/octet-stream")
        else:
            body = json.dumps(data, indent=2, default=str).encode("utf-8")
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, ContentType="application/json")

        return {"status": "success"}

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchBucket":
            raise FileNotFoundError(f"Bucket {bucket_name} not found")
        raise

    

