import boto3
import os


AWS_PROFILE_NAME = "nlightnlabs"

def get_s3_client(profile_name=AWS_PROFILE_NAME, environment="production"):
    if environment == "development" and profile_name:
        # Local dev – use profile from ~/.aws/credentials
        session = boto3.Session(profile_name=profile_name)
    else:
        # EC2 or Lambda – use instance role
        session = boto3.Session()

    return session.client("s3")


s3_client = get_s3_client(environment=os.getenv("ENVIRONMENT", "production"))
response = s3_client.list_buckets()
print(response)

