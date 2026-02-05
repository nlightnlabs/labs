import psycopg2
import os
import boto3
import botocore

print("====================================")
print(f"Test boto3 API")
print("====================================")

try:
    sts = boto3.client("sts")
    print("AWS identity:", sts.get_caller_identity())

except botocore.exceptions.NoCredentialsError:
    print("No AWS credentials found in container!\n")

try:
    rds = boto3.client("rds")
    resp = rds.describe_db_instances(DBInstanceIdentifier="nlightnlabsdev01-postgres")
    print(f"DB Instances:\n")
    print(f"{resp['DBInstances'][0]['Endpoint']}\n")

except Exception as e:
    print("Unable to access RDS:\n {e}")


print("====================================")
print(f"Test to database connection")
print("====================================")

DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")
DBDATABASE = os.getenv("DBDATABASE")

print(f"""
Connecting using pyscopg2 with the following credentials:\n 
      DBHOST: {DBHOST}\n 
      DBUSER: {DBUSER}\n 
      DBPASSWORD: {DBPASSWORD}\n 
      DBDATABASE: {DBDATABASE}
""")

try:
    conn = psycopg2.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPASSWORD,
        dbname=DBDATABASE,
        connect_timeout=10
    )
    print(f"Direct Connection successful!\n")

    query = "SELECT * FROM USERS;"
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    print(f"First 5 records:\n")
    print(rows[0:5])
    conn.close()

except Exception as e:
    print(f"Unable to connect to RDS:\n{e}")

