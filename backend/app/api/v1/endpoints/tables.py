"""
Generic Tables CRUD API endpoints.

This module provides CRUD operations for database tables using the postgres_db utility functions.
Supports dynamic table management, including listing tables, fetching data, and performing CRUD operations.
"""

from typing import Optional, List, Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.utilities.postgres_db import (
    DbQueryModel,
    db_query,
    db_table,
    db_list,
    get_list_of_tables,
    insert_records,
    update_records,
    delete_records,
    db_connect,
)
from app.config import get_tenant_state

router = APIRouter()


# ============== Request/Response Schemas ==============

class TableListRequest(BaseModel):
    """Request schema for listing tables."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"


class TableListResponse(BaseModel):
    """Response schema for table list."""
    tables: List[str]
    count: int


class TableDataRequest(BaseModel):
    """Request schema for fetching table data."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"
    table_name: str


class RecordCreateRequest(BaseModel):
    """Request schema for creating records."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"
    table_name: str
    records: List[Dict[str, Any]]
    data_model: Optional[Dict[str, Any]] = None


class RecordUpdateRequest(BaseModel):
    """Request schema for updating records."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"
    table_name: str
    records: List[Dict[str, Any]]
    data_model: Optional[Dict[str, Any]] = None
    where_clause: Optional[List[Dict[str, Any]]] = None


class RecordDeleteRequest(BaseModel):
    """Request schema for deleting records."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"
    table_name: str
    records: Optional[List[Dict[str, Any]]] = None
    where_clause: Optional[List[Dict[str, Any]]] = None


class QueryRequest(BaseModel):
    """Request schema for raw SQL queries."""
    db_name: Optional[str] = None
    query: str


class UniqueValuesRequest(BaseModel):
    """Request schema for getting unique values from a field."""
    db_name: Optional[str] = None
    db_schema: Optional[str] = "data"
    table_name: str
    field_name: str


# ============== Helper Functions ==============

def get_db_config():
    """Get database configuration from tenant state."""
    state = get_tenant_state()
    return {
        "db_host": state.DBHOST,
        "db_user": state.DBUSER,
        "db_port": str(state.DBPORT),
        "db_name": state.DEFAULTDB,
    }


# ============== Endpoints ==============

@router.get("/list", response_model=TableListResponse)
async def list_all_tables(
    db_schema: Optional[str] = "data",
    db_name: Optional[str] = None,
):
    """
    List all tables in the specified schema.

    Returns a list of table names available in the database schema.
    """
    config = get_db_config()

    try:
        conn = await db_connect(
            db_host=config["db_host"],
            db_port=config["db_port"],
            db_user=config["db_user"],
            db_name=db_name or config["db_name"],
        )

        if conn is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to database"
            )

        try:
            tables = await get_list_of_tables(conn, db_schema)
            return TableListResponse(tables=tables, count=len(tables))
        finally:
            await conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tables: {str(e)}"
        )


@router.post("/data")
async def get_table_data(request: TableDataRequest):
    """
    Get all data from a specific table.

    Returns all rows from the specified table with proper serialization.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        db_schema=request.db_schema,
        table_name=request.table_name,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await db_table(db_request)
        return {"success": True, "data": result, "count": len(result) if isinstance(result, list) else 0}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching table data: {str(e)}"
        )


@router.post("/query")
async def execute_query(request: QueryRequest):
    """
    Execute a raw SQL query.

    Supports SELECT, INSERT, UPDATE, DELETE, and DDL statements.
    Use with caution - this endpoint allows direct SQL execution.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        query=request.query,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await db_query(db_request)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing query: {str(e)}"
        )


@router.post("/records/create")
async def create_records(request: RecordCreateRequest):
    """
    Create new records in a table.

    Supports batch insertion with automatic type conversion based on data_model.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        db_schema=request.db_schema,
        table_name=request.table_name,
        records=request.records,
        data_model=request.data_model,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await insert_records(db_request)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return {"success": True, "data": result, "count": len(result) if isinstance(result, list) else 0}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating records: {str(e)}"
        )


@router.post("/records/update")
async def update_table_records(request: RecordUpdateRequest):
    """
    Update existing records in a table.

    Can update by record ID or using a where clause for bulk updates.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        db_schema=request.db_schema,
        table_name=request.table_name,
        records=request.records,
        data_model=request.data_model,
        where_clause=request.where_clause,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await update_records(db_request)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return {"success": True, "data": result, "count": len(result) if isinstance(result, list) else 0}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating records: {str(e)}"
        )


@router.post("/records/delete")
async def delete_table_records(request: RecordDeleteRequest):
    """
    Delete records from a table.

    Can delete by record ID or using a where clause for bulk deletion.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        db_schema=request.db_schema,
        table_name=request.table_name,
        records=request.records,
        where_clause=request.where_clause,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await delete_records(db_request)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return {"success": True, "data": result, "count": len(result) if isinstance(result, list) else 0}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting records: {str(e)}"
        )


@router.post("/unique-values")
async def get_unique_values(request: UniqueValuesRequest):
    """
    Get unique values from a specific field in a table.

    Useful for populating dropdown filters and selection options.
    """
    config = get_db_config()

    db_request = DbQueryModel(
        db_name=request.db_name or config["db_name"],
        db_schema=request.db_schema,
        table_name=request.table_name,
        field_name=request.field_name,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await db_list(db_request)
        return {"success": True, "data": result or [], "field": request.field_name}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching unique values: {str(e)}"
        )


@router.get("/schema/{table_name}")
async def get_table_schema(
    table_name: str,
    db_schema: Optional[str] = "data",
    db_name: Optional[str] = None,
):
    """
    Get the schema (column definitions) for a specific table.

    Returns column names, data types, and constraints.
    """
    config = get_db_config()

    query = f"""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = '{db_schema}'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position;
    """

    db_request = DbQueryModel(
        db_name=db_name or config["db_name"],
        query=query,
        db_host=config["db_host"],
        db_user=config["db_user"],
        db_port=config["db_port"],
    )

    try:
        result = await db_query(db_request)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        columns = []
        for row in result:
            columns.append({
                "name": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
                "maxLength": row["character_maximum_length"],
            })

        return {"success": True, "table": table_name, "columns": columns}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching table schema: {str(e)}"
        )
