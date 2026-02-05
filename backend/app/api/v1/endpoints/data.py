"""Data Tables API endpoints for portfolio company data management."""

from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from pydantic import BaseModel, Field

from app.utils.database import get_db
from app.models import Portco
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.dependencies import (
    get_current_user, CurrentUser, get_portco_access, PortcoAccess,
    require_detailed_access
)

router = APIRouter()


# ============== Schemas ==============

class DataType(str, Enum):
    """Column data types."""
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


class ColumnInfo(BaseModel):
    """Schema for column information."""
    name: str
    displayName: str
    dataType: DataType
    nullable: bool


class TableInfo(BaseModel):
    """Schema for table information."""
    name: str
    displayName: str
    rowCount: int
    columns: List[ColumnInfo]
    lastUpdated: datetime


class TableDataResponse(BaseModel):
    """Schema for table data response."""
    columns: List[ColumnInfo]
    rows: List[Dict[str, Any]]
    totalRows: int


class CellUpdate(BaseModel):
    """Schema for updating a single cell."""
    rowId: str
    column: str
    value: Any


class FilterCondition(BaseModel):
    """Schema for filter conditions."""
    column: str
    operator: str  # eq, neq, gt, gte, lt, lte, contains, startsWith, endsWith
    value: Any


class SortCondition(BaseModel):
    """Schema for sort conditions."""
    column: str
    direction: str = "asc"  # asc or desc


# ============== Helper Functions ==============

def get_portco_or_404(db: Session, portco_id: str) -> Portco:
    """Get a portfolio company by ID or raise 404."""
    portco = db.query(Portco).filter(Portco.id == portco_id).first()
    if not portco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio company not found"
        )
    return portco


def infer_data_type(pg_type: str) -> DataType:
    """Infer the data type from PostgreSQL type."""
    pg_type = pg_type.lower()

    if any(t in pg_type for t in ['int', 'numeric', 'decimal', 'float', 'double', 'real']):
        return DataType.NUMBER
    elif any(t in pg_type for t in ['date', 'time', 'timestamp']):
        return DataType.DATE
    elif 'bool' in pg_type:
        return DataType.BOOLEAN
    else:
        return DataType.STRING


def snake_to_title(name: str) -> str:
    """Convert snake_case to Title Case."""
    return ' '.join(word.capitalize() for word in name.split('_'))


# ============== Endpoints ==============

@router.get("/tables/{portco_id}", response_model=APIResponse[List[TableInfo]])
async def list_tables(
    portco_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all data tables for a portfolio company.

    Returns table names, row counts, column info, and last update times.
    Uses the data_tables registry to get the list of tables.
    """
    # Validate portco exists and user has access
    portco = get_portco_or_404(db, portco_id)

    schema_name = "data"

    try:
        # Query the data_tables registry for this portco's tables
        registry_query = text("""
            SELECT
                dt.id,
                dt.table_name,
                dt.display_name,
                dt.description,
                dt.row_count,
                dt.column_count,
                dt.created_at,
                dt.updated_at
            FROM data.data_tables dt
            WHERE dt.portco_id = :portco_id::uuid
            AND dt.is_active = true
            ORDER BY dt.created_at DESC
        """)

        result = db.execute(registry_query, {"portco_id": portco_id})
        registry_tables = result.fetchall()

        tables = []
        for row in registry_tables:
            table_name = row[1]
            display_name = row[2]
            row_count = row[4] or 0
            last_updated = row[7] or row[6] or datetime.utcnow()

            # Get column info from the actual table
            columns_query = text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = :schema
                AND table_name = :table
                AND column_name NOT LIKE '\\_%'
                ORDER BY ordinal_position
            """)

            cols_result = db.execute(columns_query, {"schema": schema_name, "table": table_name})
            columns = []
            for col in cols_result.fetchall():
                columns.append(ColumnInfo(
                    name=col[0],
                    displayName=snake_to_title(col[0]),
                    dataType=infer_data_type(col[1]),
                    nullable=col[2] == 'YES'
                ))

            tables.append(TableInfo(
                name=table_name,
                displayName=display_name or snake_to_title(table_name),
                rowCount=int(row_count),
                columns=columns,
                lastUpdated=last_updated
            ))

        # If no tables found from registry, return empty list (no more mock data)
        return APIResponse(
            success=True,
            data=tables,
            meta={"message": f"Found {len(tables)} tables"}
        )

    except Exception as e:
        # Log error but try to return empty list
        import traceback
        print(f"Error fetching tables: {e}")
        traceback.print_exc()
        return APIResponse(
            success=True,
            data=[],
            meta={"message": f"Error: {str(e)}"}
        )


@router.get("/tables/{portco_id}/{table_name}", response_model=APIResponse[TableDataResponse])
async def get_table_data(
    portco_id: str,
    table_name: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_column: Optional[str] = None,
    sort_direction: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get data from a specific table for a portfolio company.

    Supports pagination, sorting, and filtering.
    The table_name should be the actual table name in the data schema.
    """
    # Validate portco exists and user has access
    portco = get_portco_or_404(db, portco_id)

    schema_name = "data"

    try:
        # Verify table exists in the registry for this portco
        registry_query = text("""
            SELECT id FROM data.data_tables
            WHERE table_name = :table_name
            AND portco_id = :portco_id::uuid
            AND is_active = true
        """)
        registry_check = db.execute(registry_query, {
            "table_name": table_name,
            "portco_id": portco_id
        }).fetchone()

        # Also check if table exists in database
        check_query = text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = :schema AND table_name = :table
            )
        """)
        exists = db.execute(check_query, {"schema": schema_name, "table": table_name}).scalar()

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' not found"
            )

        # Get column info (exclude internal columns)
        columns_query = text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position
        """)
        cols_result = db.execute(columns_query, {"schema": schema_name, "table": table_name})
        columns = []
        for col in cols_result.fetchall():
            columns.append(ColumnInfo(
                name=col[0],
                displayName=snake_to_title(col[0]),
                dataType=infer_data_type(col[1]),
                nullable=col[2] == 'YES'
            ))

        # Get total count (filtered by portco_id)
        count_query = text(f'SELECT COUNT(*) FROM {schema_name}."{table_name}" WHERE _portco_id = :portco_id::uuid')
        total_rows = db.execute(count_query, {"portco_id": portco_id}).scalar()

        # Build data query with sorting
        order_clause = "ORDER BY id"
        if sort_column:
            # Validate sort column exists
            valid_columns = [c.name for c in columns]
            if sort_column in valid_columns:
                order_clause = f'ORDER BY "{sort_column}" {sort_direction.upper()}'

        data_query = text(f'''
            SELECT * FROM {schema_name}."{table_name}"
            WHERE _portco_id = :portco_id::uuid
            {order_clause}
            LIMIT :limit OFFSET :offset
        ''')

        result = db.execute(data_query, {"portco_id": portco_id, "limit": limit, "offset": offset})
        rows = [dict(row._mapping) for row in result.fetchall()]

        # Convert any non-serializable values
        for row in rows:
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
                elif isinstance(value, UUID):
                    row[key] = str(value)

        return APIResponse(
            success=True,
            data=TableDataResponse(
                columns=columns,
                rows=rows,
                totalRows=total_rows
            ),
            meta={
                "offset": offset,
                "limit": limit,
                "hasMore": offset + limit < total_rows
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error fetching table data: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching table data: {str(e)}"
        )


@router.put("/tables/{portco_id}/{table_name}/cell", response_model=APIResponse[dict])
async def update_cell(
    portco_id: str,
    table_name: str,
    update: CellUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a single cell value in a table.

    Requires the row ID and column name.
    The table_name should be the actual table name in the data schema.
    """
    # Validate portco exists and user has access
    portco = get_portco_or_404(db, portco_id)

    schema_name = "data"

    try:
        # Validate table and column exist
        check_query = text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table AND column_name = :column
        """)
        exists = db.execute(check_query, {
            "schema": schema_name,
            "table": table_name,
            "column": update.column
        }).fetchone()

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{update.column}' not found in table '{table_name}'"
            )

        # Update the cell (ensure row belongs to this portco)
        update_query = text(f'''
            UPDATE {schema_name}."{table_name}"
            SET "{update.column}" = :value,
                "_updated_at" = CURRENT_TIMESTAMP
            WHERE id = :row_id
            AND _portco_id = :portco_id::uuid
            RETURNING id
        ''')

        result = db.execute(update_query, {
            "value": update.value,
            "row_id": update.rowId,
            "portco_id": portco_id
        })
        updated = result.fetchone()

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Row with ID '{update.rowId}' not found or does not belong to this portfolio company"
            )

        db.commit()

        return APIResponse(
            success=True,
            data={
                "rowId": update.rowId,
                "column": update.column,
                "newValue": update.value
            },
            meta={"message": "Cell updated successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cell: {str(e)}"
        )


# ============== Mock Data Helpers ==============

def get_mock_tables() -> List[TableInfo]:
    """Generate mock tables for development."""
    return [
        TableInfo(
            name="trial_balance",
            displayName="Trial Balance",
            rowCount=1250,
            lastUpdated=datetime(2026, 1, 28, 14, 30, 0),
            columns=[
                ColumnInfo(name="account_id", displayName="Account ID", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="account_name", displayName="Account Name", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="debit", displayName="Debit", dataType=DataType.NUMBER, nullable=True),
                ColumnInfo(name="credit", displayName="Credit", dataType=DataType.NUMBER, nullable=True),
                ColumnInfo(name="balance", displayName="Balance", dataType=DataType.NUMBER, nullable=False),
                ColumnInfo(name="period_date", displayName="Period Date", dataType=DataType.DATE, nullable=False),
            ]
        ),
        TableInfo(
            name="revenue_breakdown",
            displayName="Revenue Breakdown",
            rowCount=845,
            lastUpdated=datetime(2026, 1, 27, 10, 0, 0),
            columns=[
                ColumnInfo(name="product_id", displayName="Product ID", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="product_name", displayName="Product Name", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="revenue", displayName="Revenue", dataType=DataType.NUMBER, nullable=False),
                ColumnInfo(name="units_sold", displayName="Units Sold", dataType=DataType.NUMBER, nullable=True),
                ColumnInfo(name="region", displayName="Region", dataType=DataType.STRING, nullable=True),
                ColumnInfo(name="sale_date", displayName="Sale Date", dataType=DataType.DATE, nullable=False),
            ]
        ),
        TableInfo(
            name="customer_list",
            displayName="Customer List",
            rowCount=328,
            lastUpdated=datetime(2026, 1, 26, 9, 0, 0),
            columns=[
                ColumnInfo(name="customer_id", displayName="Customer ID", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="customer_name", displayName="Customer Name", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="revenue", displayName="Revenue", dataType=DataType.NUMBER, nullable=False),
                ColumnInfo(name="contract_start", displayName="Contract Start", dataType=DataType.DATE, nullable=True),
                ColumnInfo(name="contract_end", displayName="Contract End", dataType=DataType.DATE, nullable=True),
                ColumnInfo(name="is_active", displayName="Active", dataType=DataType.BOOLEAN, nullable=False),
            ]
        ),
        TableInfo(
            name="ap_aging",
            displayName="AP Aging",
            rowCount=156,
            lastUpdated=datetime(2026, 1, 25, 15, 0, 0),
            columns=[
                ColumnInfo(name="vendor_id", displayName="Vendor ID", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="vendor_name", displayName="Vendor Name", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="invoice_number", displayName="Invoice #", dataType=DataType.STRING, nullable=False),
                ColumnInfo(name="amount", displayName="Amount", dataType=DataType.NUMBER, nullable=False),
                ColumnInfo(name="due_date", displayName="Due Date", dataType=DataType.DATE, nullable=False),
                ColumnInfo(name="days_overdue", displayName="Days Overdue", dataType=DataType.NUMBER, nullable=True),
            ]
        ),
    ]


def get_mock_table_data(table_name: str) -> TableDataResponse:
    """Generate mock table data for development."""
    mock_tables = get_mock_tables()
    table_info = next((t for t in mock_tables if t.name == table_name), mock_tables[0])

    rows = []
    num_rows = min(100, table_info.rowCount)

    import random

    for i in range(num_rows):
        row = {"id": i + 1}
        for col in table_info.columns:
            if col.dataType == DataType.STRING:
                if "id" in col.name:
                    row[col.name] = f"{col.name.upper()[:3]}-{str(i + 1).zfill(4)}"
                elif "name" in col.name:
                    row[col.name] = f"{col.displayName} {i + 1}"
                elif "region" in col.name:
                    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
                    row[col.name] = regions[i % len(regions)]
                elif "invoice" in col.name:
                    row[col.name] = f"INV-{str(i + 1000).zfill(6)}"
                else:
                    row[col.name] = f"Value {i + 1}"
            elif col.dataType == DataType.NUMBER:
                if any(x in col.name for x in ["revenue", "amount", "balance"]):
                    row[col.name] = round(random.random() * 1000000, 2)
                elif any(x in col.name for x in ["debit", "credit"]):
                    row[col.name] = round(random.random() * 100000, 2) if random.random() > 0.5 else None
                elif any(x in col.name for x in ["units", "days"]):
                    row[col.name] = random.randint(0, 1000)
                else:
                    row[col.name] = round(random.random() * 10000, 2)
            elif col.dataType == DataType.DATE:
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                row[col.name] = f"2025-{str(month).zfill(2)}-{str(day).zfill(2)}"
            elif col.dataType == DataType.BOOLEAN:
                row[col.name] = random.random() > 0.3
        rows.append(row)

    return TableDataResponse(
        columns=table_info.columns,
        rows=rows,
        totalRows=table_info.rowCount
    )
