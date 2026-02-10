# Enhance `DataPage.tsx`: Integrate Field Metadata for Dynamic Column Behavior

## Objective

Enhance the existing `DataPage.tsx` component so that when a user selects a data table, the app also fetches the corresponding **field metadata** from PostgreSQL and uses it to dynamically control how each column behaves in the UI (e.g., editability, sorting, filtering, visibility).

---

## Context

### Current Behavior

- A left-side menu lists all available tables from the PostgreSQL `data` schema.
- Selecting a table queries and renders its records in a data table.
- Users can perform CRUD operations: read, edit, add, delete records.
- Users can upload/import files into the database.

### Desired Behavior

- When a table is selected, the app fetches **two** things:
  1. The actual records from `data.<table_name>`
  2. The field-level metadata from `field_meta_data.<table_name>`
- The field metadata controls how each column renders and behaves before the table is displayed in the table.  For example, the meta data table contains fields like "ui_table_viewable", "ui_table_filterable", "ui_table_editable", "ui_table_sortable".  There is also a "default_values" and default_options

---

## PostgreSQL Schema Layout

| Schema            | Purpose                                | Example Table               |
| ----------------- | -------------------------------------- | --------------------------- |
| `data`            | Contains the actual data tables        | `data.users`, `data.orders` |
| `field_metadata`  | Contains per-field metadata for each table | `field_metadata.users`, `field_metadata.orders` |

Each row in a `field_metadata` table describes **one field/column** from the corresponding `data` table, with properties controlling UI behavior.

---

## Instructions

### Step 1: Inspect the Existing Codebase

Before writing any code:

- Read `DataPage.tsx` and all related components, hooks, API routes, and utility files to understand the current data-fetching flow, state management, and table rendering logic.
- Identify where table selection triggers a data fetch, and where/how columns are configured for the rendered table.
- Note the libraries and patterns already in use (e.g., state management, API client, table component).

### Step 2: Inspect the `field_metadata` Schema

Query the PostgreSQL `field_metadata` schema to discover:

- The actual column names and data types in the metadata tables.
- What properties are available (e.g., `editable`, `sortable`, `filterable`, `visible`, `display_name`, `column_order`, etc.).
- Do **not** assume property names — use the actual structure found in the database.

### Step 3: Fetch Field Metadata Alongside Data

When a user selects a table (e.g., `users`):

1. Query `data.users` for the records (existing behavior).
2. **Also** query `field_metadata.users` for the column metadata.
3. These can be fetched in parallel or sequentially — follow whichever pattern the codebase already uses for data fetching.

### Step 4: Build a Column Configuration from Metadata

Before rendering the data table:

1. Parse the field metadata results into a column configuration map (keyed by field/column name).
2. Apply metadata properties to control column behavior. Examples:
   - **`editable`** → If `false`, the column is read-only (no inline editing, no edit in forms/modals).
   - **`sortable`** → If `true`, enable sorting on the column header.
   - **`filterable`** → If `true`, enable filtering for the column.
   - **`visible`** → If `false`, hide the column from the table entirely.
   - **`display_name`** → Use as the column header label instead of the raw field name.
   - **`column_order`** → Use to control the display order of columns.
3. Adapt the above to match whatever properties actually exist in the `field_metadata` tables (per Step 2).

### Step 5: Graceful Fallback

- If no corresponding `field_metadata.<table_name>` table exists for a selected data table, **fall back to the current default behavior** (all columns editable, sortable, etc.).
- Handle this gracefully — no errors or broken UI if metadata is missing.

### Step 6: Preserve All Existing Functionality

All current features must continue to work without regression:

- CRUD operations (create, read, update, delete records)
- File upload and import
- Table selection from the left menu
- All existing UI interactions

The field metadata integration **layers on top** of existing behavior — it refines it, not replaces it.

---

## Constraints

- Follow the existing code conventions, file structure, and patterns in the project.
- Use the same libraries, API patterns, and state management approach already in the codebase.
- Do not introduce new dependencies unless absolutely necessary.
- Keep the component clean and maintainable — extract helpers or hooks if the logic becomes complex.
