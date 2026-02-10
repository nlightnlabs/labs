
import os
from dotenv import load_dotenv
import importlib
import pandas as pd
import json
import time
from typing import Optional, Dict, Any, List
from pydantic import Field
import uvicorn
from openai import OpenAI


#Libraries for asynchronouse api calls
from fastapi import FastAPI, Request, HTTPException, Body, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import httpx
import asyncio


from pydantic import BaseModel, EmailStr


#import utilitie functions
from .utilities.encryption import hash_text, match_encrypted_text
from .utilities import postgres_db as pgdb
from .utilities import email_utils as email_utils
from .utilities import claude  as claude
from .utilities import aws_s3 as aws_s3
from .utilities import two_fa as two_fa

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

from .config import (
    ENVIRONMENT, IS_PRODUCTION, AWS_REGION, AWS_PROFILE,
    TENANT_NAME, DBHOST, DBUSER, DBPORT, DEFAULTDB,
    S3_BUCKET, S3_ROOT_PREFIX, set_tenant_config
)

DEFAULT_DB = DEFAULTDB  # Alias for backward compatibility

# Initialize the Flask application
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Default Server Side Template Rendering
@app.get("/", response_class=HTMLResponse)
async def render_page(request: Request):

    context = {
        "appName": "Hosting",
        "webserver": "FastAPI",
        "currentPage": "index"
    }

    return JSONResponse(context)

# Test api connection
@app.get("/test", response_class=JSONResponse)
async def api_test():
    print("running test...")
    sample_data = {
        'name': 'FastAPI Web Server',
        'version': '1.0',
        'status': 'running',
    }
    return JSONResponse(sample_data)


@app.get("/health")
def health():
    return {"status": "ok"}


#Encrtyption Utilities Routes ########################################################################################


@app.post("/utilities/encrypt")
async def encrypt(text: Optional[str] = Body(...), method: Optional[str] = Body(...)):
    hashed = hash_text(text, method)
    return hashed

@app.post("/utilities/verify")
async def encrypt(text: Optional[str] = Body(...), encrypted_text: Optional[str] = Body(...), method: Optional[str] = Body(...)):
    result = match_encrypted_text(text, encrypted_text, method)
    return result


#General Postgres Database Routes ########################################################################################

import logging

logger = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO)

from urllib.parse import urlparse

def get_globals():
    # Import module directly and access attributes to get updated values after set_tenant_config
    from . import config as cfg
    result = {
        "tenant_name": cfg.TENANT_NAME,
        "db_host": cfg.DBHOST,
        "db_user": cfg.DBUSER,
        "db_name": cfg.DEFAULTDB,
        "s3_bucket": cfg.S3_BUCKET,
        "s3_root_prefix": cfg.S3_ROOT_PREFIX
    }
    print(f"🔍 DEBUG - get_globals returning db_name: '{cfg.DEFAULTDB}'")
    return result
  

# Determine Tenant #
@app.post("/tenant_config")
async def get_tenant_info(request: Request):

    print("Getting tenant info...")

    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        raise HTTPException(400, "Missing Origin/Referer header")

    parsed = urlparse(origin)
    hostname = parsed.hostname

    print(f"hostname: {hostname}")

    if not hostname:
        raise HTTPException(400, "Invalid Origin header")

    # LOCAL / SHARED DB
    if "localhost" in origin:
        # Read db_name directly from environment to avoid import-time binding issues
        local_db_name = os.getenv('DEFAULT_DB_NLIGHTNLABS', 'base_tenant_main')
        print(f"🔍 DEBUG - localhost detected")
        print(f"🔍 DEBUG - DEFAULTDB variable (import-time): '{DEFAULTDB}'")
        print(f"🔍 DEBUG - local_db_name (env lookup): '{local_db_name}'")
        print(f"🔍 DEBUG - TENANT_NAME: '{TENANT_NAME}'")
        print(f"🔍 DEBUG - DBHOST: '{DBHOST}'")
        set_tenant_config(
            tenant_name=TENANT_NAME,
            db_host=DBHOST,
            db_name=local_db_name,  # Use env lookup instead of DEFAULTDB
            s3_bucket=S3_BUCKET,
            s3_root_prefix=S3_ROOT_PREFIX
        )

    else:
        tenant_name = hostname.split(".")[0]
        print(f"tenant_name: {tenant_name}")

        lookup = pgdb.DbQueryModel(
            db_host="tenant-rds.clwbltzci0fj.us-west-1.rds.amazonaws.com",
            db_user=DBUSER,
            db_name="base",
            query=f"""
                SELECT *
                FROM data.tenants
                WHERE tenant_name = '{tenant_name}'
            """
        )

        rows = await pgdb.db_query(lookup)

        if rows is None:
            raise HTTPException(500, "Database connection failed")

        if isinstance(rows, dict) and "error" in rows:
            raise HTTPException(500, rows["error"])

        if not rows:
            raise HTTPException(404, f"Tenant not found: {tenant_name}")

        tenant = rows[0]

        set_tenant_config(
            tenant_name=tenant["tenant_name"],
            db_host=tenant["rds_endpoint"],
            db_name=tenant["database_name"],
            s3_bucket=tenant["s3_bucket"],
            s3_root_prefix=tenant["s3_root_prefix"]
        )

    result = get_globals()
    print(f"tenant config: {result}")

    return result



#General database query:  Reroute to imported function
@app.post("/db/query")
async def db_query(payload: pgdb.DbQueryModel,http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(request=http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]

    return await pgdb.db_query(payload)


#Table Query:  Reroute to imported function
@app.post("/db/table")
async def db_table(payload: pgdb.DbQueryModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(request=http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        
    return await pgdb.db_table(payload)



#Get list of unique values from a field in a database table
@app.post("/db/list")
async def db_list(payload: pgdb.DbQueryModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(request=http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = "data"
    return await pgdb.db_list(payload)

#Insert a new record into database
@app.post("/db/insert")
async def insert_records(payload: pgdb.DbQueryModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(request=http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = "data"
    return await pgdb.insert_records(payload)

#Update records in a database table
@app.post("/db/update")
async def update_records(payload: pgdb.DbQueryModel, http_request: Request):
    print(f"📥 /db/update received payload:")
    print(f"   table_name: {payload.table_name}")
    print(f"   records: {payload.records}")
    print(f"   scope: {payload.scope}")

    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(request=http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = "data"
        print(f"   db_host: {payload.db_host}")
        print(f"   db_name: {payload.db_name}")

    result = await pgdb.update_records(payload)
    print(f"📤 /db/update result: {result}")
    return result

#Delete records from a database table
@app.delete("/db/delete")
async def delete_records(payload: pgdb.DbQueryModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = "data"
    return await pgdb.delete_records(payload)


#User Records Database Routes #########################################################################################
@app.post("/db/authenticate_user")
async def authenticate_user(
    payload: pgdb.UserModel,
    http_request: Request
):
    print("Payload")
    print(payload)

    if payload.scope and payload.scope == "tenant":
        globals = get_globals()
        print("globals")
        print(globals)
        payload.db_host = globals["db_host"]
        payload.db_name = globals["db_name"]
        payload.db_schema = "data"

    return await pgdb.authenticate_user(payload)


#Create a new user
@app.post("/db/create_user")
async def create_user(payload: pgdb.UserModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = tenant.get("db_schema", payload.db_schema)
    return await pgdb.create_user(payload)


@app.post("/db/edit_user")
async def edit_user(payload: pgdb.UserModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = tenant.get("db_schema", payload.db_schema)
    return await pgdb.edit_user(payload)


@app.post("/db/reset_password")
async def reset_password(payload: pgdb.UserModel, http_request: Request):
    if payload.scope and payload.scope =="tenant":
        tenant = await get_tenant_info(http_request)
        payload.db_host = tenant["db_host"]
        payload.db_name = tenant["db_name"]
        payload.db_schema = tenant.get("db_schema", payload.db_schema)
    return await pgdb.reset_password(payload)



# _______________________________________________________________________________________________
# AWS S3
# _______________________________________________________________________________________________

@app.post("/s3/list_folders")
async def list_folders(payload: aws_s3.S3PrefixModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    return await aws_s3.list_folders(payload)

@app.post("/s3/list_files")
async def list_files(payload: aws_s3.S3PrefixModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    return await aws_s3.list_files(payload)

@app.post("/s3/fetch_files")
async def fetch_files(payload: aws_s3.S3KeyModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    return await aws_s3.fetch_files(payload)

@app.post("/s3/download_files")
async def download_files(payload: aws_s3.S3KeyModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    return await aws_s3.download_files(payload)


@app.post("/s3/upload_files")
async def upload_files(payload: aws_s3.S3PrefixModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    return await aws_s3.upload_files(payload)


@app.post("/s3/save_json_data_file")
async def save_json_data_file(payload: aws_s3.S3KeyModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    response  = await aws_s3.save_json_data_file(payload)
    return response

@app.post("/s3/delete_files")
async def delete_files(payload: aws_s3.S3KeyModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    response  = await aws_s3.save_json_data_file(payload)
    return await response


@app.post("/s3/save_data_in_s3")
async def save_json_data_file(payload: aws_s3.S3KeyModel, http_request: Request):
    if payload.scope and payload.scope == "tenant":
        tenant = await get_tenant_info(http_request)
        payload.bucket_name = tenant["s3_bucket"]
        root = tenant["s3_root_prefix"]
        payload.prefix = f"{root}/{payload.prefix}"
    response  = await aws_s3.save_json_data_file(payload)
    return response


@app.post("/s3/upload_from_browser")
async def upload_from_browser(
    http_request: Request,
    files: List[UploadFile] = File(...),
    relative_paths: List[str] = Form(...)
):
    """
    Generic endpoint to upload one or more files from the browser to S3.

    Args:
        files: List of files uploaded from the browser (via FormData)
        relative_paths: List of relative paths where each file will be stored
                       e.g., ["images/123-johndoe/avatar", "documents/report"]
                       Extensions are auto-appended from original filenames if not provided.
                       Must have same length as files list.

    Returns:
        - status: "success" (all uploaded), "partial" (some failed), "error" (all failed)
        - uploaded: List of successfully uploaded files with file_path and s3_key
        - failed: List of failed uploads with error details
        - total: Total number of files
        - success_count: Number of successfully uploaded files
    """
    try:
        # Validate that files and relative_paths have the same length
        if len(files) != len(relative_paths):
            raise HTTPException(
                status_code=400,
                detail=f"Number of files ({len(files)}) must match number of relative_paths ({len(relative_paths)})"
            )

        # Get tenant info for bucket and root prefix
        tenant = await get_tenant_info(http_request)
        bucket_name = tenant["s3_bucket"]
        root_prefix = tenant["s3_root_prefix"].rstrip("/")

        # Prepare file list for the upload function
        files_to_upload = []
        file_paths = []  # Track relative paths for response

        for file, relative_path in zip(files, relative_paths):
            # Get original filename and extension
            original_filename = file.filename or "file"
            ext = os.path.splitext(original_filename)[1].lower()

            # If relative_path doesn't include extension, append it
            if not os.path.splitext(relative_path)[1]:
                file_path = f"{relative_path}{ext}"
            else:
                file_path = relative_path

            # Construct full S3 key: {s3_root_prefix}/{relative_path}
            s3_key = f"{root_prefix}/{file_path}"

            # Read file content
            file_content = await file.read()

            files_to_upload.append({
                "file_content": file_content,
                "file_name": original_filename,
                "s3_key": s3_key
            })
            file_paths.append(file_path)

        # Upload all files to S3
        upload_result = await aws_s3.upload_from_browser_to_s3(
            files=files_to_upload,
            bucket_name=bucket_name
        )

        # Add file_path to each uploaded file info for database storage
        # Create a mapping of s3_key to file_path for quick lookup
        s3_key_to_file_path = {
            file_info["s3_key"]: file_paths[idx]
            for idx, file_info in enumerate(files_to_upload)
        }
        for uploaded_file in upload_result.get("uploaded", []):
            uploaded_file["file_path"] = s3_key_to_file_path.get(uploaded_file["s3_key"])

        return {
            "status": upload_result["status"],
            "uploaded": upload_result.get("uploaded", []),
            "failed": upload_result.get("failed", []),
            "total": upload_result.get("total", 0),
            "success_count": upload_result.get("success_count", 0),
            "message": f"Uploaded {upload_result.get('success_count', 0)} of {upload_result.get('total', 0)} files"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading files from browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# _______________________________________________________________________________________________
# Call an App
# _______________________________________________________________________________________________




# Define request model for validation
class RunAppRequest(BaseModel):
    app_name: str  # Python file/app name without .py
    main_function: str  # Function to call within the module
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Parameters to pass to the function

# Function to dynamically import and run an app function (Synchronous)
def import_app(filepath: str, app_name: str, function: str, parameters: Dict[str, Any]):
    try:
        # Import the module dynamically
        module = importlib.import_module(f"{filepath}.{app_name}")

        # Get the function dynamically
        func = getattr(module, function)

        # Call the function with parameters
        return func(**parameters) if parameters else func()

    except Exception as e:
        raise RuntimeError(f"Error importing or executing {app_name}.{function}: {str(e)}")


# FastAPI endpoint to run a Python app (Fully Asynchronous)
@app.post("/runApp")
async def run_app(request: RunAppRequest):
    filepath = "apps"  # Directory where your apps are stored

    print("running app...")

    if not request.app_name or not request.main_function:
        raise HTTPException(status_code=400, detail="Module name and function name are required")

    try:
        # Run import_app asynchronously using asyncio.to_thread (non-blocking)
        result = await asyncio.to_thread(import_app, filepath, request.app_name, request.main_function, request.parameters)
       
        print(f"Result from app: {result}")

        # Handle different response types
        if result is not None:
            if isinstance(result, (dict, list)):
                return result  # FastAPI automatically converts JSON-serializable data
            elif isinstance(result, pd.DataFrame):
                return result.to_dict(orient="records")  # Convert DataFrame to JSON
            else:
                return {"result": str(result)}  # Convert other types to string
        else:
            raise HTTPException(status_code=404, detail="No data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing app function: {str(e)}")



# Define request model for validation
class OpenAIRequest(BaseModel):
    prompt: str
    data: Optional[Dict[str, Any]] = None
    model: str = "gpt-4"
    temperature: float = 0


class Attachment(BaseModel):
    name: str
    type: str
    size: int
    lastModified: int
    content: str


#Send Email
@app.post("/send_email")
async def send_email(request: email_utils.EmailPayload):
    print(request)
    try:
        result = email_utils.send_email(request)
        print("Printing the result")
        print(result)
        return {"status": "success", "id": result["id"], "detail": f"Email sent to {', '.join(request.to_email)}"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/claude_ask")
def call_claude_ask(request: claude.GeneralQueryModel):
    try:
        result = claude.ask(request)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/claude_classify")
def call_claude_classify(request: claude.ClassifyModel):
    try:
        result = claude.classify(request)
        return {"classified_data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/map_fields")
async def map_fields_endpoint(request: claude.FieldMappingModel):
    try:
        return claude.map_fields(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Two-Factor Authentication Routes ########################################################################################

class TwoFASetupRequest(BaseModel):
    user_id: str
    method: str  # sms, email, authenticator, backup_codes
    contact_info: Optional[str] = None

class TwoFAVerifyRequest(BaseModel):
    user_id: str
    method: str
    verification_code: str

class TwoFADisableRequest(BaseModel):
    user_id: str
    verification_code: Optional[str] = None

class TwoFAValidateRequest(BaseModel):
    user_id: str
    code: str

@app.post("/2fa/setup")
async def setup_2fa_endpoint(request: TwoFASetupRequest):
    """Initialize 2FA setup for a user"""
    try:
        result = await two_fa.setup_2fa(
            user_id=request.user_id,
            method=request.method,
            contact_info=request.contact_info
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/2fa/verify")
async def verify_2fa_endpoint(request: TwoFAVerifyRequest):
    """Verify 2FA setup with a code"""
    try:
        result = await two_fa.verify_2fa_setup(
            user_id=request.user_id,
            method=request.method,
            verification_code=request.verification_code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/2fa/disable")
async def disable_2fa_endpoint(request: TwoFADisableRequest):
    """Disable 2FA for a user"""
    try:
        result = await two_fa.disable_2fa(
            user_id=request.user_id,
            verification_code=request.verification_code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/2fa/status/{user_id}")
async def get_2fa_status_endpoint(user_id: str):
    """Get 2FA status for a user"""
    try:
        result = await two_fa.get_2fa_status(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/2fa/validate")
async def validate_2fa_endpoint(request: TwoFAValidateRequest):
    """Validate a 2FA code during login"""
    try:
        result = await two_fa.validate_2fa_code(
            user_id=request.user_id,
            code=request.code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = 8000
    uvicorn.run(
        "main:app",
        host="localhost",
        port=port,
        reload=True,
        log_level="info"
    )


