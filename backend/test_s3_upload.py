#!/usr/bin/env python3
"""
Test script to verify S3 upload functionality.

Run from the labs/backend directory:
    python test_s3_upload.py

Or with verbose output:
    python test_s3_upload.py --verbose
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """Print a success message."""
    print(f"  ✅ {text}")


def print_error(text: str):
    """Print an error message."""
    print(f"  ❌ {text}")


def print_info(text: str):
    """Print an info message."""
    print(f"  ℹ️  {text}")


def test_configuration(verbose: bool = False):
    """Test S3 configuration."""
    print_header("Checking S3 Configuration")

    from app.core.config import settings, S3_BUCKET, S3_ROOT_PREFIX, AWS_REGION, AWS_PROFILE

    config = {
        "STORAGE_PROVIDER": settings.STORAGE_PROVIDER,
        "AWS_S3_BUCKET": settings.AWS_S3_BUCKET,
        "AWS_S3_REGION": settings.AWS_S3_REGION,
        "AWS_S3_PREFIX": settings.AWS_S3_PREFIX,
        "AWS_PROFILE": settings.AWS_PROFILE,
        "S3_BUCKET (env)": S3_BUCKET,
        "S3_ROOT_PREFIX (env)": S3_ROOT_PREFIX,
        "AWS_REGION (env)": AWS_REGION,
        "AWS_PROFILE (env)": AWS_PROFILE,
        "ENVIRONMENT": settings.ENVIRONMENT,
    }

    print("\n  Current Configuration:")
    for key, value in config.items():
        print(f"    {key}: {value}")

    # Check for issues
    issues = []

    if settings.STORAGE_PROVIDER != "aws_s3":
        issues.append(f"STORAGE_PROVIDER is '{settings.STORAGE_PROVIDER}', not 'aws_s3'")

    if not settings.AWS_S3_BUCKET and not S3_BUCKET:
        issues.append("S3 bucket is not configured")

    if not settings.AWS_S3_REGION and not AWS_REGION:
        issues.append("AWS region is not configured")

    if issues:
        print("\n  ⚠️  Configuration Issues:")
        for issue in issues:
            print(f"    - {issue}")
        return False, config
    else:
        print_success("Configuration looks good!")
        return True, config


def test_aws_credentials(verbose: bool = False):
    """Test AWS credentials."""
    print_header("Testing AWS Credentials")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        from app.core.config import settings, AWS_PROFILE, AWS_REGION

        profile = AWS_PROFILE or settings.AWS_PROFILE
        region = AWS_REGION or settings.AWS_S3_REGION or "us-west-2"

        print(f"\n  Using profile: {profile or 'default'}")
        print(f"  Using region: {region}")

        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        else:
            session = boto3.Session(region_name=region)

        sts = session.client('sts')
        identity = sts.get_caller_identity()

        print_success(f"Authenticated as: {identity['Arn']}")
        print_info(f"Account: {identity['Account']}")

        return True, session

    except NoCredentialsError:
        print_error("No AWS credentials found!")
        print_info("Please configure AWS credentials:")
        print_info("  - Set AWS_PROFILE_ILLUMINIS environment variable")
        print_info("  - Or run: aws configure --profile illuminis")
        return False, None

    except ClientError as e:
        print_error(f"AWS authentication failed: {e}")
        return False, None

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False, None


def test_bucket_access(session, verbose: bool = False):
    """Test S3 bucket access."""
    print_header("Testing S3 Bucket Access")

    from app.core.config import settings, S3_BUCKET

    bucket = settings.AWS_S3_BUCKET or S3_BUCKET

    if not bucket:
        print_error("No S3 bucket configured!")
        return False

    print(f"\n  Bucket: {bucket}")

    try:
        s3 = session.client('s3')

        # Check if bucket exists and we have access
        s3.head_bucket(Bucket=bucket)
        print_success(f"Bucket '{bucket}' exists and is accessible")

        # List some objects to verify read access
        response = s3.list_objects_v2(Bucket=bucket, MaxKeys=5)
        count = response.get('KeyCount', 0)
        print_info(f"Found {count} objects in bucket (limited to 5)")

        if verbose and count > 0:
            print("\n  Sample objects:")
            for obj in response.get('Contents', []):
                print(f"    - {obj['Key']} ({obj['Size']} bytes)")

        return True

    except Exception as e:
        print_error(f"Bucket access failed: {e}")
        return False


def test_upload(session, verbose: bool = False):
    """Test uploading a file to S3."""
    print_header("Testing S3 Upload")

    from app.core.config import settings, S3_BUCKET, S3_ROOT_PREFIX

    bucket = settings.AWS_S3_BUCKET or S3_BUCKET
    prefix = settings.AWS_S3_PREFIX or S3_ROOT_PREFIX or ""

    # Create test data
    test_content = {
        "test": True,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "S3 upload test from Illuminis",
        "data": [1, 2, 3, 4, 5]
    }
    test_data = json.dumps(test_content, indent=2).encode('utf-8')

    # Create test key
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    test_key = f"{prefix.rstrip('/')}/_test/s3_upload_test_{timestamp}.json"

    print(f"\n  Bucket: {bucket}")
    print(f"  Key: {test_key}")
    print(f"  Size: {len(test_data)} bytes")

    try:
        s3 = session.client('s3')

        # Upload the file
        s3.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=test_data,
            ContentType='application/json'
        )
        print_success("File uploaded successfully!")

        # Verify the file exists
        response = s3.head_object(Bucket=bucket, Key=test_key)
        print_success(f"Verified file exists (ETag: {response['ETag']})")

        # Generate presigned URL
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': test_key},
            ExpiresIn=3600
        )
        print_info(f"Presigned URL (valid 1 hour):\n    {url[:100]}...")

        # Clean up - delete the test file
        s3.delete_object(Bucket=bucket, Key=test_key)
        print_success("Test file cleaned up")

        return True

    except Exception as e:
        print_error(f"Upload failed: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        return False


def test_storage_provider(verbose: bool = False):
    """Test the storage provider abstraction."""
    print_header("Testing Storage Provider Module")

    from app.core.config import settings

    # First, check if STORAGE_PROVIDER is set to aws_s3
    if settings.STORAGE_PROVIDER != "aws_s3":
        print_info(f"STORAGE_PROVIDER is '{settings.STORAGE_PROVIDER}'")
        print_info("Forcing aws_s3 provider for this test...")

    try:
        from app.utils.storage import get_storage_provider, AWSS3Provider

        # Force AWS S3 provider
        provider = get_storage_provider("aws_s3")

        print(f"\n  Provider type: {type(provider).__name__}")
        print(f"  Bucket: {provider.bucket}")
        print(f"  Prefix: {provider.prefix}")
        print(f"  Region: {provider.region}")

        # Test upload using the provider
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        test_path = f"_test/provider_test_{timestamp}.txt"
        test_content = f"Test upload at {datetime.utcnow().isoformat()}"

        print(f"\n  Uploading test file: {test_path}")
        url = provider.upload(test_content.encode(), test_path, "text/plain")
        print_success(f"Upload successful!")
        print_info(f"URL: {url[:80]}...")

        # Verify it exists
        exists = provider.exists(test_path)
        print_success(f"File exists check: {exists}")

        # Delete test file
        provider.delete(test_path)
        print_success("Test file deleted")

        return True

    except Exception as e:
        print_error(f"Storage provider test failed: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        return False


def main():
    """Run all S3 tests."""
    parser = argparse.ArgumentParser(description="Test S3 upload functionality")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  S3 Upload Test Script")
    print("=" * 60)

    results = {}

    # Test 1: Configuration
    config_ok, config = test_configuration(args.verbose)
    results["Configuration"] = config_ok

    # Test 2: AWS Credentials
    creds_ok, session = test_aws_credentials(args.verbose)
    results["AWS Credentials"] = creds_ok

    if session:
        # Test 3: Bucket Access
        bucket_ok = test_bucket_access(session, args.verbose)
        results["Bucket Access"] = bucket_ok

        if bucket_ok:
            # Test 4: Direct Upload
            upload_ok = test_upload(session, args.verbose)
            results["Direct Upload"] = upload_ok

    # Test 5: Storage Provider Module
    provider_ok = test_storage_provider(args.verbose)
    results["Storage Provider"] = provider_ok

    # Summary
    print_header("Test Summary")
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n  🎉 All tests passed! S3 uploads should work.")
    else:
        print("\n  ⚠️  Some tests failed. Check the errors above.")
        print("\n  Common fixes:")
        print("    1. Set STORAGE_PROVIDER=aws_s3 in .env")
        print("    2. Configure AWS credentials: aws configure --profile illuminis")
        print("    3. Set AWS_PROFILE_ILLUMINIS=illuminis in .env")
        print("    4. Ensure S3_BUCKET_ILLUMINIS is set correctly")

    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
