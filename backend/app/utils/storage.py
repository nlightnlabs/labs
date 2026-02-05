"""Storage utilities for file operations with AWS S3 or Azure Blob."""

import os
from typing import Optional, List, BinaryIO
from dataclasses import dataclass

from app.config import get_tenant_state


class StorageError(Exception):
    """Exception raised for storage operation errors."""
    pass


@dataclass
class FileInfo:
    """Information about a stored file."""
    key: str
    size: int
    last_modified: Optional[str] = None
    content_type: Optional[str] = None


# Global storage provider instance
_storage_provider = None


def get_storage_provider():
    """Get the current storage provider."""
    global _storage_provider
    if _storage_provider is None:
        _storage_provider = S3StorageProvider()
    return _storage_provider


def reset_storage_provider():
    """Reset the storage provider (useful when tenant config changes)."""
    global _storage_provider
    _storage_provider = None


class S3StorageProvider:
    """AWS S3 storage provider."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy-load S3 client."""
        if self._client is None:
            import boto3
            from app.config import IS_PRODUCTION, _DEFAULT_AWS_PROFILE, _DEFAULT_AWS_REGION

            if IS_PRODUCTION:
                session = boto3.Session()
            else:
                session = boto3.Session(profile_name=_DEFAULT_AWS_PROFILE)

            self._client = session.client('s3', region_name=_DEFAULT_AWS_REGION)
        return self._client

    @property
    def bucket(self) -> str:
        """Get the S3 bucket name."""
        state = get_tenant_state()
        return state.S3_BUCKET

    @property
    def prefix(self) -> str:
        """Get the S3 key prefix for this tenant."""
        state = get_tenant_state()
        return state.S3_ROOT_PREFIX

    def _full_key(self, key: str) -> str:
        """Get full S3 key including tenant prefix."""
        return f"{self.prefix}{key}"


async def upload_file(
    file: BinaryIO,
    key: str,
    content_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Upload a file to storage.

    Args:
        file: File-like object to upload
        key: Storage key/path for the file
        content_type: MIME type of the file
        metadata: Optional metadata to attach

    Returns:
        The storage URL/key of the uploaded file
    """
    provider = get_storage_provider()
    full_key = provider._full_key(key)

    try:
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if metadata:
            extra_args['Metadata'] = metadata

        provider.client.upload_fileobj(
            file,
            provider.bucket,
            full_key,
            ExtraArgs=extra_args if extra_args else None
        )
        return full_key
    except Exception as e:
        raise StorageError(f"Failed to upload file: {str(e)}")


async def download_file(key: str) -> bytes:
    """
    Download a file from storage.

    Args:
        key: Storage key/path of the file

    Returns:
        File contents as bytes
    """
    provider = get_storage_provider()
    full_key = provider._full_key(key)

    try:
        import io
        buffer = io.BytesIO()
        provider.client.download_fileobj(provider.bucket, full_key, buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        raise StorageError(f"Failed to download file: {str(e)}")


async def delete_file(key: str) -> bool:
    """
    Delete a file from storage.

    Args:
        key: Storage key/path of the file

    Returns:
        True if successful
    """
    provider = get_storage_provider()
    full_key = provider._full_key(key)

    try:
        provider.client.delete_object(Bucket=provider.bucket, Key=full_key)
        return True
    except Exception as e:
        raise StorageError(f"Failed to delete file: {str(e)}")


async def list_files(prefix: str = "") -> List[FileInfo]:
    """
    List files in storage.

    Args:
        prefix: Optional prefix to filter files

    Returns:
        List of FileInfo objects
    """
    provider = get_storage_provider()
    full_prefix = provider._full_key(prefix)

    try:
        response = provider.client.list_objects_v2(
            Bucket=provider.bucket,
            Prefix=full_prefix
        )

        files = []
        for obj in response.get('Contents', []):
            files.append(FileInfo(
                key=obj['Key'].replace(provider.prefix, ''),
                size=obj['Size'],
                last_modified=obj['LastModified'].isoformat() if obj.get('LastModified') else None
            ))
        return files
    except Exception as e:
        raise StorageError(f"Failed to list files: {str(e)}")
