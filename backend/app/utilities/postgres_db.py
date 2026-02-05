import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import asyncpg
import psycopg2
import boto3
import ssl
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv


# Utilities from your project
from .pgdtconversion import convert_data_type
from .encryption import hash_text, match_encrypted_text


# ============================================================================
# LOAD ENV
# ============================================================================

from .. import globals as gb
ENVIRONMENT = gb.ENVIRONMENT
IS_PRODUCTION = gb.IS_PRODUCTION

AWS_REGION = gb.AWS_REGION
AWS_PROFILE = gb.AWS_PROFILE
TENANT_NAME = gb.TENANT_NAME
DBHOST = gb.DBHOST
DBUSER = gb.DBUSER
DBPORT = gb.DBPORT
DEFAULT_DB = gb.DEFAULT_DB
S3_BUCKET = gb.S3_BUCKET
S3_ROOT_PREFIX = gb.S3_ROOT_PREFIX


# ============================================================================
# AWS SESSION FIX
# ============================================================================

def get_boto_session(profile: str=AWS_PROFILE) -> boto3.Session:
    if IS_PRODUCTION:
        return boto3.Session()
    else:
        print(f"\nAWS Profile: {profile}\n")
        return boto3.Session(profile_name=profile)


async def encrypt_text(text, method):
    hashed = hash_text(text, method)
    return hashed

async def verify_encryption(text, encrypted_text, method):
    result = match_encrypted_text(text, encrypted_text, method)
    return result


# Fetch List of All Tables in the Database (with optional schema)
async def get_list_of_tables(db: asyncpg.Connection, db_schema: Optional[str] = None):
    print("print(db_schema function:")
    print("db_schema:",db_schema)
    print("db:",db)

    if db_schema:
        query = """
        SELECT schemaname || '.' || tablename AS full_table_name
        FROM pg_tables
        WHERE schemaname = $1;
        """
        result = await db.fetch(query, db_schema)
    else:
        query = """
        SELECT schemaname || '.' || tablename AS full_table_name
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        result = await db.fetch(query)

    return [row["full_table_name"] for row in result]


def serialize_value(value):
    """Ensure all data types are properly formatted for JSON serialization."""
    if isinstance(value, datetime):
        return value.isoformat() 
    elif isinstance(value, Decimal):
        return float(value) 
    elif isinstance(value, dict) or isinstance(value, list):
        return json.loads(json.dumps(value))  
    return value  



BASE_DIR = Path(__file__).resolve().parent


def build_ssl_context():
    cafile = BASE_DIR / "certs/global-bundle.pem"
    ctx = ssl.create_default_context(cafile=str(cafile))
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    print(f"[SSL] Using CA file (dev): {cafile}")
    return ctx


async def generate_rds_token(db_host:str = DBHOST, db_port:str = DBPORT, db_user: str = DBUSER, region:str=AWS_REGION):

    try:
        session = get_boto_session()
        print("[TOKEN] Boto session profile:", session.profile_name)

        rds = session.client("rds", region_name=AWS_REGION)

        token = rds.generate_db_auth_token(
            DBHostname=db_host,
            Port=db_port,
            DBUsername=db_user,
            Region=region
        )

        if not token or not isinstance(token, str):
            print("[TOKEN ERROR] Token was NONE or invalid")
            raise RuntimeError("IAM token generation failed (None returned)")
        
        print("[TOKEN] Token returned:", f"{len(token)} chars")
        return token
    
    except Exception as e:
        print(f"Unable to generate password token for database {e}")
        return None


async def db_connect(db_host, db_port, db_user, db_name):

    print(f"db_host {db_host}\n")
    print(f"db_port {db_port}\n")
    print(f"db_user {db_user}\n")
    print(f"db_name {db_name}\n")
    
    password_token = await generate_rds_token(db_host=db_host, db_port=db_port, db_user=db_user, region=AWS_REGION)
    ssl_context=build_ssl_context()

    try:
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=password_token,
            database=db_name,
            ssl=ssl_context
        )
    
        return conn
    
    except Exception as e:
        print(f"\nUnable to connect to database\n {e}")

# Request Model for Database Query
class DbQueryModel(BaseModel):
    db_name: Optional[str] = DEFAULT_DB
    db_schema: Optional[str] = "data"
    table_name: Optional[str] = None
    field_name: Optional[str] = None
    data_model: Optional[Dict[str, Any]] = None
    records: Optional[List[Dict[str,Any]]] = None
    where_clause: Optional[List[Dict[str,Any]]] = None
    query: Optional[str] = None
    db_host: Optional[str] = DBHOST
    db_user: Optional[str] = DBUSER
    db_port: Optional[str] = DBPORT
    scope: Optional[str] = None


async def db_query(request: DbQueryModel):
    if not request.query:
        return {"error": "Missing SQL query"}

    sql = request.query.strip()
    sql_lower = sql.lower()

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        # -------------------------------
        # SELECT → fetch rows
        # -------------------------------
        if sql_lower.startswith("select"):
            rows = await conn.fetch(sql)
            return [
                {k: serialize_value(v) for k, v in dict(row).items()}
                for row in rows
            ]

        # -------------------------------
        # EVERYTHING ELSE → execute
        # (DROP / CREATE / INSERT / UPDATE / DELETE / TRIGGER / EXTENSION)
        # -------------------------------
        else:
            result = await conn.execute(sql)
            return {
                "status": "OK",
                "result": result
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "sql": sql[:500]  # truncated for safety
        }

    finally:
        await conn.close()

    

# Select entire table from a database
async def db_table(request: DbQueryModel):

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        full_table_name = f"{request.db_schema}.{request.table_name}"

        rows = await conn.fetch(f"SELECT * FROM {full_table_name};")

        return [
            {k: serialize_value(v) for k, v in dict(r).items()}
            for r in rows
        ]
    finally:
        await conn.close()


#Get list of unique values from a field in a database table
async def db_list(request: DbQueryModel):
    field_name = request.field_name
    db_schema = request.db_schema
    table_name = request.table_name

    query = f"""
        SELECT array_agg(DISTINCT {field_name}) AS result
        FROM {db_schema}.{table_name};
    """

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        values = await conn.fetchval(query)
        return values
    finally:
        await conn.close()



async def get_autogenerated_fields(
    conn: asyncpg.Connection,
    table_name: str,
    meta_schema: str = "field_meta_data",
):
    meta_table = f"{meta_schema}.{table_name}_meta_data"

    try:
        rows = await conn.fetch(f"""
            SELECT
                field_name,
                LOWER(COALESCE(automation, '')) AS automation,
                LOWER(COALESCE(primary_key, 'false')) AS primary_key
            FROM {meta_table};
        """)
    except Exception:
        return set()

    autogenerated = set()

    for r in rows:
        is_pk = r["primary_key"] == "true"
        automation = r["automation"]

        if (
            is_pk
            or "gen_random_uuid" in automation
            or "current_timestamp" in automation
            or "auto_update" in automation
        ):
            autogenerated.add(r["field_name"])

    return autogenerated


# Get information schema for a table including data types
async def get_table_column_types(conn: asyncpg.Connection, schema: str, table: str):
    
    rows = await conn.fetch(
        """
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = $1
          AND table_name = $2;
        """,
        schema,
        table,
    )

    return {
        r["column_name"]: r["data_type"]
        for r in rows
    }


# Create Records
async def insert_records(request: DbQueryModel):
    records = request.records or []
    data_model = request.data_model or {}

    # Normalize data_model (list → dict)
    if isinstance(data_model, list):
        data_model = {
            item["field_name"]: item
            for item in data_model
            if "field_name" in item
        }

    if not records:
        return {"error": "No records provided for insert"}

    full_table_name = f"{request.db_schema}.{request.table_name}"

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        async with conn.transaction():

            # Validate table exists
            allowable_tables = await get_list_of_tables(conn, request.db_schema)
            if full_table_name not in allowable_tables:
                return {"error": f"Table '{full_table_name}' does not exist."}

            # Identify autogenerated fields
            autogenerated_fields = await get_autogenerated_fields(conn,request.table_name)

            # 🔹 Fetch schema to ensure proper data types
            column_types = await get_table_column_types(conn, request.db_schema,request.table_name)

            inserted_rows = []

            for record in records:
                clean = {}

                for field, value in record.items():

                    # Skip autogenerated fields
                    if field in autogenerated_fields:
                        continue

                    if value is None:
                        continue

                    model_entry = data_model.get(field, {})

                    # Verify if field is encrypted
                    encrypt_flag = model_entry.get("encrypt")
                    if isinstance(encrypt_flag, str):
                        encrypt_flag = encrypt_flag.strip().lower() in {"true", "1", "yes"}

                    if encrypt_flag is True:
                        value = hash_text(str(value), "bcrypt")
                    # Explicit metadata type
                    elif model_entry.get("data_type"):
                        value = convert_data_type(value, model_entry["data_type"])
                    # Fallback to Postgres schema
                    elif field in column_types:
                        postgres_type = column_types[field]
                        value = convert_data_type(value, postgres_type)

                    # Else: leave value as-is (last resort)

                    clean[field] = value

                if not clean:
                    continue

                columns = list(clean.keys())
                values = [clean[col] for col in columns]

                placeholders = ", ".join(
                    f"${i + 1}" for i in range(len(values))
                )
                column_clause = ", ".join(columns)

                sql = f"""
                    INSERT INTO {full_table_name}
                    ({column_clause})
                    VALUES ({placeholders})
                    RETURNING *;
                """

                try:
                    row = await conn.fetchrow(sql, *values)
                    print(f"Row Inserted:\n{row}")
                except Exception as e:
                    print(f"Unable to insert record. {e}\nRecord: {record}")
                    row = None

                if row:
                    inserted_rows.append(
                        {k: serialize_value(v) for k, v in dict(row).items()}
                    )

            return inserted_rows

    finally:
        await conn.close()



#Update records in a database table
async def update_records(request: DbQueryModel):
    records = request.records or []
    data_model = request.data_model or {}
    where_clause = request.where_clause

    # Normalize data_model (list → dict)
    if isinstance(data_model, list):
        data_model = {
            item["field_name"]: item
            for item in data_model
            if "field_name" in item
        }

    if not records:
        return {"error": "No records provided for update"}

    full_table_name = f"{request.db_schema}.{request.table_name}"

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        async with conn.transaction():

            # Validate table exists
            allowable_tables = await get_list_of_tables(conn, request.db_schema)
            if full_table_name not in allowable_tables:
                return {"error": f"Table '{full_table_name}' does not exist."}

            # Identify autogenerated fields
            autogenerated_fields = await get_autogenerated_fields(
                conn, request.table_name
            )

            # Fetch schema types ONCE
            column_types = await get_table_column_types(
                conn, request.db_schema, request.table_name
            )

            # ----------------------------------------
            # Determine UPDATE MODE
            # ----------------------------------------
            ids = [r.get("id") for r in records if r.get("id") is not None]
            use_id_mode = len(ids) == len(records) and len(records) > 0

            if not use_id_mode and not where_clause:
                return {
                    "error": "Either all records must include 'id' or a where_clause must be provided."
                }

            # ----------------------------------------
            # Determine updateable fields
            # ----------------------------------------
            update_fields = sorted({
                k
                for r in records
                for k in r.keys()
                if k not in autogenerated_fields and k != "id"
            })

            if not update_fields:
                return {"error": "No updatable fields provided"}

            params = []
            idx = 1

            # ----------------------------------------
            # Build SET clause
            # ----------------------------------------
            if use_id_mode:
                case_blocks = {f: [] for f in update_fields}

                for r in records:
                    rid = r["id"]

                    for field in update_fields:
                        if field not in r:
                            continue

                        value = r[field]
                        if value is None or value == "":
                            continue

                        model_entry = data_model.get(field, {})

                        # Verify if field is encrypted
                        encrypt_flag = model_entry.get("encrypt")
                        if isinstance(encrypt_flag, str):
                            encrypt_flag = encrypt_flag.strip().lower() in {"true", "1", "yes"}

                        if encrypt_flag:
                            value = hash_text(str(value), "bcrypt")
                        elif model_entry.get("data_type"):
                            value = convert_data_type(value, model_entry["data_type"])
                        elif field in column_types:
                            value = convert_data_type(value, column_types[field])

                        case_blocks[field].append(
                            f"WHEN id = ${idx} THEN ${idx + 1}"
                        )
                        params.extend([rid, value])
                        idx += 2

                set_clause = ", ".join(
                    f"{f} = CASE {' '.join(v)} ELSE {f} END"
                    for f, v in case_blocks.items()
                    if v
                )

                id_placeholders = ", ".join(
                    f"${idx + i}" for i in range(len(ids))
                )
                params.extend(ids)

                where_sql = f"id IN ({id_placeholders})"

            # ----------------------------------------
            # WHERE-CLAUSE MODE
            # ----------------------------------------
            else:
                assignments = []

                record = records[0]  # single payload
                for field in update_fields:
                    value = record.get(field)
                    if value is None or value == "":
                        continue

                    model_entry = data_model.get(field, {})

                    encrypt_flag = model_entry.get("encrypt")
                    if isinstance(encrypt_flag, str):
                        encrypt_flag = encrypt_flag.lower() in {"true", "1", "yes"}

                    if encrypt_flag:
                        value = hash_text(str(value), "bcrypt")
                    elif model_entry.get("data_type"):
                        value = convert_data_type(value, model_entry["data_type"])
                    elif field in column_types:
                        value = convert_data_type(value, column_types[field])

                    assignments.append(f"{field} = ${idx}")
                    params.append(value)
                    idx += 1

                set_clause = ", ".join(assignments)

                # Build WHERE clause
                where_parts = []
                for clause in where_clause:
                    sub_parts = []
                    for key, val in clause.items():
                        sub_parts.append(f"{key} = ${idx}")
                        params.append(val)
                        idx += 1
                    where_parts.append(f"({' AND '.join(sub_parts)})")

                where_sql = " OR ".join(where_parts)

            # ----------------------------------------
            # Final SQL
            # ----------------------------------------
            sql = f"""
                UPDATE {full_table_name}
                SET {set_clause}
                WHERE {where_sql}
                RETURNING *;
            """

            rows = await conn.fetch(sql, *params)

            return [
                {k: serialize_value(v) for k, v in dict(r).items()}
                for r in rows
            ]

    finally:
        await conn.close()



# Delete records in a database table
async def delete_records(request: DbQueryModel):
    records = request.records or []
    where_clause = request.where_clause

    full_table_name = f"{request.db_schema}.{request.table_name}"

    conn = await db_connect(
        db_host=request.db_host,
        db_port=request.db_port,
        db_user=request.db_user,
        db_name=request.db_name
    )

    try:
        async with conn.transaction():
            # Validate table exists
            allowable_tables = await get_list_of_tables(conn, request.db_schema)
            if full_table_name not in allowable_tables:
                return {"error": f"Table '{full_table_name}' does not exist."}

            ids = [r.get("id") for r in records if r.get("id") is not None]
            use_id_mode = len(ids) == len(records) and len(records) > 0

            if not use_id_mode and not where_clause:
                return {
                    "error": "Either all records must include 'id' or a where_clause must be provided."
                }

            params = []
            idx = 1

            if use_id_mode:
                id_placeholders = ", ".join(f"${idx + i}" for i in range(len(ids)))
                params.extend(ids)
                where_sql = f"id IN ({id_placeholders})"
            else:
                where_parts = []
                for clause in where_clause:
                    sub_parts = []
                    for key, val in clause.items():
                        sub_parts.append(f"{key} = ${idx}")
                        params.append(val)
                        idx += 1
                    where_parts.append(f"({' AND '.join(sub_parts)})")
                where_sql = " OR ".join(where_parts)

            sql = f"""
                DELETE FROM {full_table_name}
                WHERE {where_sql}
                RETURNING *;
            """

            rows = await conn.fetch(sql, *params)
            return [
                {k: serialize_value(v) for k, v in dict(r).items()}
                for r in rows
            ]
    finally:
        await conn.close()



# Base model for user model
class UserModel(BaseModel):
    user_record: Optional[Dict[str, Any]] = None
    db_name: Optional[str] = DEFAULT_DB
    db_schema: Optional[str] = "data"
    table_name: Optional[str] = "users"
    data_model: Optional[Dict[str, Any]] = None
    db_host: Optional[str] = DBHOST
    db_user: Optional[str] = DBUSER
    db_port: Optional[str] = DBPORT
    scope: Optional[str] = None



async def authenticate_user(request: UserModel):
    user_record = request.user_record or {}
    db_schema = request.db_schema
    table_name = request.table_name

    print(request.db_host)
    print(request.db_port)
    print(request.db_user)
    print(request.db_name)

    if not user_record.get("username") or not user_record.get("password"):
        return {
            "validation": False,
            "message": "Username and password are required"
        }

    full_table_name = f"{db_schema}.{table_name}"

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        # Fetch user by username
        query = f"""
            SELECT *
            FROM {full_table_name}
            WHERE username = $1;
        """

        row = await conn.fetchrow(query, user_record["username"])


        if not row:
            return {"validation": False, "message": "Invalid username or password"}

        user = dict(row)
        print(f"\nuser record retrieved: {user}\n")

        stored_hashed_password = user.get("password")
        provided_password = user_record["password"]

        # Validate password
        if not match_encrypted_text(
            provided_password,
            stored_hashed_password,
            "bcrypt"
        ):
            return {"validation": False, "message": "Invalid username or password"}

        # Remove password before returning
        user.pop("password", None)

        sanitized_user = {
            key: serialize_value(value)
            for key, value in user.items()
        }

        return {
            "validation": True,
            "user": sanitized_user
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "validation": False,
            "message": "Authentication failed",
            "error": str(e)
        }

    finally:
        await conn.close()



# Create a new user
async def create_user(request: UserModel):
    user_record = request.user_record or {}
    data_model = request.data_model or {}
    db_schema = request.db_schema
    table_name = request.table_name or "users"

    # Normalize data_model (list → dict)
    if isinstance(data_model, list):
        data_model = {
            item["field_name"]: item
            for item in data_model
            if "field_name" in item
        }


    # Validation
    username = user_record.get("username")
    password = user_record.get("password")

    if not username or not password:
        return {
            "status_code": 400,
            "status": "ERROR",
            "validation": False,
            "message": "username and password are required",
        }

    full_table_name = f"{db_schema}.{table_name}"

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        async with conn.transaction():

            # --------------------------------------------------
            # 2. Validate table exists
            # --------------------------------------------------
            allowable_tables = await get_list_of_tables(conn, db_schema)
            if full_table_name not in allowable_tables:
                return {
                    "status_code": 400,
                    "status": "ERROR",
                    "validation": False,
                    "message": f"Table '{full_table_name}' does not exist",
                }


            # Fetch autogenerated fields + schema types
            autogenerated_fields = await get_autogenerated_fields(
                conn, table_name
            )

            column_types = await get_table_column_types(
                conn, db_schema, table_name
            )


            # Normalize payload (type-safe)
            clean = {}

            for field, value in user_record.items():

                # Skip autogenerated fields
                if field in autogenerated_fields:
                    continue

                # Skip empty values
                if value is None or value == "":
                    continue

                # Password handled separately
                if field == "password":
                    continue

                model_entry = data_model.get(field, {})

                # Metadata type
                if model_entry.get("data_type"):
                    value = convert_data_type(value, model_entry["data_type"])

                # Fallback to Postgres schema
                elif field in column_types:
                    value = convert_data_type(value, column_types[field])

                clean[field] = value


            # Always hash password (special case)
            if len(str(password).encode("utf-8")) > 72:
                return {
                    "status_code": 400,
                    "status": "ERROR",
                    "validation": False,
                    "message": "Password exceeds bcrypt 72-byte limit",
                }

            clean["password"] = hash_text(str(password), "bcrypt")

            if not clean:
                return {
                    "status_code": 400,
                    "status": "ERROR",
                    "validation": False,
                    "message": "No valid fields provided for user creation",
                }


            # Insert
            columns = sorted(clean.keys())
            values = [clean[col] for col in columns]

            placeholders = ", ".join(
                f"${i + 1}" for i in range(len(values))
            )
            column_clause = ", ".join(columns)

            sql = f"""
                INSERT INTO {full_table_name}
                ({column_clause})
                VALUES ({placeholders})
                RETURNING *;
            """

            result = await conn.fetchrow(sql, *values)

            if not result:
                return {
                    "status_code": 500,
                    "status": "ERROR",
                    "validation": False,
                    "message": "User creation failed",
                }

            inserted_user = dict(result)
            inserted_user.pop("password", None)

            return {
                "status_code": 200,
                "status": "OK",
                "validation": True,
                "user": {
                    k: serialize_value(v)
                    for k, v in inserted_user.items()
                },
            }

    except asyncpg.UniqueViolationError:
        return {
            "status_code": 409,
            "status": "ERROR",
            "validation": False,
            "message": "Username already exists",
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status_code": 500,
            "status": "ERROR",
            "validation": False,
            "message": f"Error occurred: {str(e)}",
        }

    finally:
        await conn.close()

        


# Endpoint to reset password
async def reset_password(request: UserModel):
    user_record = request.user_record or {}
    db_name = request.db_name
    db_schema = request.db_schema
    table_name = request.table_name

    if not user_record.get("username") or not user_record.get("password"):
        return {
            "status_code": 400,
            "status": "ERROR",
            "validation": False,
            "message": "username and password are required",
        }

    full_table_name = f"{db_schema}.{table_name}"

    # Hash the new password
    hashed_password = hash_text(str(user_record["password"]), "bcrypt")

    query = f"""
        UPDATE {full_table_name}
        SET password = $1
        WHERE username = $2
        RETURNING *;
    """

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        async with conn.transaction():
            row = await conn.fetchrow(
                query,
                hashed_password,
                user_record["username"],
            )

        if not row:
            return {
                "status_code": 400,
                "status": "ERROR",
                "validation": False,
                "message": "User not found or update failed",
            }

        updated_user = dict(row)
        updated_user.pop("password", None)

        return {
            "status_code": 200,
            "status": "OK",
            "validation": True,
            "user": {
                key: serialize_value(value)
                for key, value in updated_user.items()
            },
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status_code": 500,
            "status": "ERROR",
            "validation": False,
            "message": f"Error occurred: {str(e)}",
        }

    finally:
        await conn.close()



        
async def edit_user(request: UserModel):
    user_record = request.user_record or {}
    data_model = request.data_model or {}

    db_name = request.db_name
    db_schema = request.db_schema
    table_name = request.table_name or "users"

    # Normalize data_model (list → dict)
    if isinstance(data_model, list):
        data_model = {
            item["field_name"]: item
            for item in data_model
            if "field_name" in item
        }

    # --------------------------------------------------
    # 1. Validation
    # --------------------------------------------------
    username = user_record.get("username")
    if not username:
        return {
            "status_code": 400,
            "validation": False,
            "message": "username is required",
        }

    full_table_name = f"{db_schema}.{table_name}"

    conn = await db_connect(
        db_host = request.db_host, 
        db_port = request.db_port, 
        db_user = request.db_user, 
        db_name = request.db_name
    )

    try:
        async with conn.transaction():

            # --------------------------------------------------
            # 2. Validate table exists
            # --------------------------------------------------
            allowable_tables = await get_list_of_tables(conn, db_schema)
            if full_table_name not in allowable_tables:
                return {
                    "status_code": 400,
                    "validation": False,
                    "message": f"Table '{full_table_name}' does not exist",
                }

            # --------------------------------------------------
            # 3. Fetch autogenerated fields + schema types
            # --------------------------------------------------
            autogenerated_fields = await get_autogenerated_fields(
                conn, table_name
            )

            column_types = await get_table_column_types(
                conn, db_schema, table_name
            )

            # --------------------------------------------------
            # 4. Normalize update payload (type-safe)
            # --------------------------------------------------
            clean = {}

            for field, value in user_record.items():

                if field == "username":
                    continue  # WHERE clause only

                if field in autogenerated_fields:
                    continue

                if value is None or value == "":
                    continue

                # Password handled separately
                if field == "password":
                    continue

                model_entry = data_model.get(field, {})

                # Metadata type
                if model_entry.get("data_type"):
                    value = convert_data_type(value, model_entry["data_type"])

                # Fallback to Postgres schema
                elif field in column_types:
                    value = convert_data_type(value, column_types[field])

                clean[field] = value

            # --------------------------------------------------
            # 5. Handle password update (special case)
            # --------------------------------------------------
            if "password" in user_record and user_record["password"] not in (None, ""):
                raw_password = str(user_record["password"])
                if len(raw_password.encode("utf-8")) > 72:
                    return {
                        "status_code": 400,
                        "validation": False,
                        "message": "Password exceeds bcrypt 72-byte limit",
                    }
                clean["password"] = hash_text(raw_password, "bcrypt")

            if not clean:
                return {
                    "status_code": 400,
                    "validation": False,
                    "message": "No valid fields provided to update",
                }

            # --------------------------------------------------
            # 6. Build UPDATE
            # --------------------------------------------------
            columns = sorted(clean.keys())
            values = [clean[col] for col in columns]

            set_clause = ", ".join(
                f"{col} = ${i + 1}" for i, col in enumerate(columns)
            )

            query = f"""
                UPDATE {full_table_name}
                SET {set_clause}
                WHERE username = ${len(columns) + 1}
                RETURNING *;
            """

            row = await conn.fetchrow(
                query,
                *values,
                username,
            )

            if not row:
                return {
                    "status_code": 404,
                    "validation": False,
                    "message": "User not found or update failed",
                }

            updated_user = dict(row)
            updated_user.pop("password", None)

            return {
                "status_code": 200,
                "validation": True,
                "message": "User updated successfully",
                "user": {
                    key: serialize_value(value)
                    for key, value in updated_user.items()
                },
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status_code": 500,
            "validation": False,
            "message": f"Error occurred: {str(e)}",
        }

    finally:
        await conn.close()



