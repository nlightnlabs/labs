import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { tablesApi, ColumnSchema } from '@/services/api';
import { FileUpload } from '@/components/common/FileUpload';
import { AddIcon, ViewIcon, DeleteIcon, UploadIcon, DownloadIcon, CloseIcon } from '@/components/icons';

interface DataPageProps {
  appName: string;
}

type SortDirection = 'asc' | 'desc' | null;

interface ColumnFilter {
  values: string[];
  isOpen: boolean;
}

interface EditingCell {
  rowId: string | number;
  column: string;
}

interface TableConfig {
  id: string;
  name: string;
  label: string;
}

interface ColumnConfig {
  key: string;
  label: string;
  editable: boolean;
  type?: string;
}

// Modal types
type ModalType = 'add' | 'view' | 'edit' | 'delete' | 'upload' | null;

export const DataPage: React.FC<DataPageProps> = () => {
  // State for tables list
  const [tableList, setTableList] = useState<TableConfig[]>([]);
  const [selectedTable, setSelectedTable] = useState<TableConfig | null>(null);
  const [isLoadingTables, setIsLoadingTables] = useState(true);

  // State for table data
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [columns, setColumns] = useState<ColumnConfig[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // Sorting and filtering
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [columnFilters, setColumnFilters] = useState<Record<string, ColumnFilter>>({});

  // Inline editing
  const [editingCell, setEditingCell] = useState<EditingCell | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const editInputRef = useRef<HTMLInputElement>(null);

  // Row selection
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set());

  // Modal state
  const [activeModal, setActiveModal] = useState<ModalType>(null);
  const [editingRecord, setEditingRecord] = useState<Record<string, unknown> | null>(null);
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [isSaving, setIsSaving] = useState(false);

  const filterRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // Fetch tables list from database
  const fetchTables = useCallback(async () => {
    setIsLoadingTables(true);
    try {
      const response = await tablesApi.listTables('data');
      const tables = response.data.tables.map((tableName: string) => {
        // Extract table name from schema.tablename format
        const name = tableName.includes('.') ? tableName.split('.')[1] : tableName;
        return {
          id: name,
          name: name,
          label: name.split('_').map((word: string) => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
        };
      });
      setTableList(tables);
      if (tables.length > 0 && !selectedTable) {
        setSelectedTable(tables[0]);
      }
    } catch (error) {
      console.error('Error fetching tables:', error);
      // Fallback to empty list
      setTableList([]);
    } finally {
      setIsLoadingTables(false);
    }
  }, [selectedTable]);

  // Fetch table data and schema
  const fetchTableData = useCallback(async (tableName: string) => {
    setIsLoadingData(true);
    try {
      // Fetch schema and data in parallel
      const [schemaResponse, dataResponse] = await Promise.all([
        tablesApi.getTableSchema(tableName, 'data'),
        tablesApi.getTableData(tableName, 'data'),
      ]);

      // Process columns from schema
      const cols: ColumnConfig[] = schemaResponse.data.columns.map((col: ColumnSchema) => ({
        key: col.name,
        label: col.name.split('_').map((word: string) => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
        editable: !['id', 'created_at', 'updated_at', '_portco_id', '_created_at', '_updated_at'].includes(col.name),
        type: col.type,
      }));
      setColumns(cols);

      // Set data
      setData(dataResponse.data.data || []);

      // Reset filters
      const emptyFilters: Record<string, ColumnFilter> = {};
      cols.forEach((col: ColumnConfig) => {
        emptyFilters[col.key] = { values: [], isOpen: false };
      });
      setColumnFilters(emptyFilters);
    } catch (error) {
      console.error('Error fetching table data:', error);
      setData([]);
      setColumns([]);
    } finally {
      setIsLoadingData(false);
    }
  }, []);

  // Load tables on mount
  useEffect(() => {
    fetchTables();
  }, [fetchTables]);

  // Load data when selected table changes
  useEffect(() => {
    if (selectedTable) {
      fetchTableData(selectedTable.name);
      setSortColumn(null);
      setSortDirection(null);
      setSelectedRows(new Set());
    }
  }, [selectedTable, fetchTableData]);

  // Close filter dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      let clickedInsideAnyFilter = false;

      Object.entries(filterRefs.current).forEach(([, ref]) => {
        if (ref && ref.contains(target)) {
          clickedInsideAnyFilter = true;
        }
      });

      if (!clickedInsideAnyFilter) {
        setColumnFilters((prev) => {
          const newFilters = { ...prev };
          Object.keys(newFilters).forEach((key) => {
            newFilters[key] = { ...newFilters[key], isOpen: false };
          });
          return newFilters;
        });
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when editing starts
  useEffect(() => {
    if (editingCell && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingCell]);

  // Get unique values for filter dropdowns
  const getUniqueValues = (column: string): string[] => {
    const values = data.map((row) => String(row[column] ?? ''));
    return Array.from(new Set(values)).filter(v => v !== '').sort();
  };

  // Handle sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortColumn(null);
        setSortDirection(null);
      }
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Handle filter toggle (multi-select)
  const handleFilterToggle = (column: string, value: string) => {
    setColumnFilters((prev) => {
      const currentValues = prev[column]?.values || [];
      const newValues = currentValues.includes(value)
        ? currentValues.filter((v) => v !== value)
        : [...currentValues, value];
      return {
        ...prev,
        [column]: { ...prev[column], values: newValues },
      };
    });
  };

  // Select all values for a column
  const handleSelectAll = (column: string) => {
    const allValues = getUniqueValues(column);
    setColumnFilters((prev) => ({
      ...prev,
      [column]: { ...prev[column], values: allValues },
    }));
  };

  // Clear all values for a column
  const handleClearColumn = (column: string) => {
    setColumnFilters((prev) => ({
      ...prev,
      [column]: { ...prev[column], values: [] },
    }));
  };

  // Toggle filter dropdown
  const toggleFilterDropdown = (column: string) => {
    setColumnFilters((prev) => {
      const newFilters = { ...prev };
      Object.keys(newFilters).forEach((key) => {
        newFilters[key] = {
          ...newFilters[key],
          isOpen: key === column ? !newFilters[key]?.isOpen : false,
        };
      });
      return newFilters;
    });
  };

  // Start editing a cell
  const startEditing = (rowId: string | number, column: string, currentValue: unknown) => {
    const colConfig = columns.find(c => c.key === column);
    if (colConfig && !colConfig.editable) return;
    setEditingCell({ rowId, column });
    setEditValue(String(currentValue ?? ''));
  };

  // Save edited value (inline edit)
  const saveEdit = async () => {
    if (!editingCell || !selectedTable) return;

    const { rowId, column } = editingCell;
    const originalRow = data.find(row => row.id === rowId);
    if (!originalRow) return;

    // Parse value based on column type
    let parsedValue: unknown = editValue;
    const colConfig = columns.find(c => c.key === column);
    if (colConfig?.type?.includes('int') || colConfig?.type?.includes('numeric')) {
      parsedValue = parseFloat(editValue) || 0;
    }

    try {
      await tablesApi.updateRecords(
        selectedTable.name,
        [{ id: rowId, [column]: parsedValue }],
        'data'
      );

      // Update local state
      setData((prev) =>
        prev.map((row) => {
          if (row.id === rowId) {
            return { ...row, [column]: parsedValue };
          }
          return row;
        })
      );
    } catch (error) {
      console.error('Error updating cell:', error);
      alert('Failed to update cell. Please try again.');
    }

    setEditingCell(null);
    setEditValue('');
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingCell(null);
    setEditValue('');
  };

  // Handle keyboard events in edit mode
  const handleEditKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      saveEdit();
    } else if (e.key === 'Escape') {
      cancelEdit();
    }
  };

  // Filter and sort data
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply filters
    Object.entries(columnFilters).forEach(([column, filter]) => {
      if (filter?.values?.length > 0) {
        result = result.filter((row) =>
          filter.values.some((v) =>
            String(row[column] ?? '').toLowerCase() === v.toLowerCase()
          )
        );
      }
    });

    // Apply sorting
    if (sortColumn && sortDirection) {
      result.sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];

        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        }

        const aStr = String(aVal ?? '').toLowerCase();
        const bStr = String(bVal ?? '').toLowerCase();

        if (sortDirection === 'asc') {
          return aStr.localeCompare(bStr);
        }
        return bStr.localeCompare(aStr);
      });
    }

    return result;
  }, [data, columnFilters, sortColumn, sortDirection]);

  // Check if any filters are active
  const hasActiveFilters = Object.values(columnFilters).some((f) => f?.values?.length > 0);

  // Get total active filter count
  const activeFilterCount = Object.values(columnFilters).reduce((acc, f) => acc + (f?.values?.length || 0), 0);

  // Clear all filters
  const clearAllFilters = () => {
    const emptyFilters: Record<string, ColumnFilter> = {};
    columns.forEach(col => {
      emptyFilters[col.key] = { values: [], isOpen: false };
    });
    setColumnFilters(emptyFilters);
  };

  // Row selection handlers
  const toggleRowSelection = (rowId: string | number) => {
    setSelectedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(rowId)) {
        newSet.delete(rowId);
      } else {
        newSet.add(rowId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedRows.size === processedData.length && processedData.length > 0) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(processedData.map((row) => row.id as string | number)));
    }
  };

  const isAllSelected = processedData.length > 0 && selectedRows.size === processedData.length;
  const isSomeSelected = selectedRows.size > 0 && selectedRows.size < processedData.length;

  // CRUD Operations
  const handleAddRecord = () => {
    setFormData({});
    setEditingRecord(null);
    setActiveModal('add');
  };

  const handleViewRecord = () => {
    if (selectedRows.size !== 1) {
      alert('Please select exactly one record to view');
      return;
    }
    const rowId = Array.from(selectedRows)[0];
    const record = data.find(row => row.id === rowId);
    if (record) {
      setEditingRecord(record);
      setFormData({ ...record });
      setActiveModal('view');
    }
  };

  const handleEditRecord = () => {
    if (selectedRows.size !== 1) {
      alert('Please select exactly one record to edit');
      return;
    }
    const rowId = Array.from(selectedRows)[0];
    const record = data.find(row => row.id === rowId);
    if (record) {
      setEditingRecord(record);
      setFormData({ ...record });
      setActiveModal('edit');
    }
  };

  const handleDeleteRecords = () => {
    if (selectedRows.size === 0) {
      alert('Please select at least one record to delete');
      return;
    }
    setActiveModal('delete');
  };

  const confirmDelete = async () => {
    if (!selectedTable || selectedRows.size === 0) return;

    setIsSaving(true);
    try {
      const recordsToDelete = Array.from(selectedRows).map(id => ({ id }));
      await tablesApi.deleteRecords(selectedTable.name, recordsToDelete, 'data');

      // Refresh data
      await fetchTableData(selectedTable.name);
      setSelectedRows(new Set());
      setActiveModal(null);
    } catch (error) {
      console.error('Error deleting records:', error);
      alert('Failed to delete records. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const saveRecord = async () => {
    if (!selectedTable) return;

    setIsSaving(true);
    try {
      if (activeModal === 'add') {
        // Create new record
        await tablesApi.createRecords(selectedTable.name, [formData], 'data');
      } else if (activeModal === 'edit' && editingRecord) {
        // Update existing record
        await tablesApi.updateRecords(
          selectedTable.name,
          [{ ...formData, id: editingRecord.id }],
          'data'
        );
      }

      // Refresh data
      await fetchTableData(selectedTable.name);
      setActiveModal(null);
      setFormData({});
      setEditingRecord(null);
    } catch (error) {
      console.error('Error saving record:', error);
      alert('Failed to save record. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFormChange = (field: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Download data as CSV
  const handleDownload = () => {
    if (!selectedTable || data.length === 0) return;

    const headers = columns.map(c => c.key).join(',');
    const rows = data.map(row =>
      columns.map(c => {
        const val = row[c.key];
        const strVal = String(val ?? '');
        // Escape quotes and wrap in quotes if contains comma
        if (strVal.includes(',') || strVal.includes('"') || strVal.includes('\n')) {
          return `"${strVal.replace(/"/g, '""')}"`;
        }
        return strVal;
      }).join(',')
    );

    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedTable.name}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Render sort icon
  const renderSortIcon = (column: string) => {
    if (sortColumn !== column) {
      return (
        <svg className="w-4 h-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    if (sortDirection === 'asc') {
      return (
        <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      );
    }
    return (
      <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  // Get status badge styles
  const getStatusBadgeClass = (value: string) => {
    const lowerValue = value.toLowerCase();
    if (['active', 'in stock', 'operational', 'paid', 'closed won', 'approved', 'received'].includes(lowerValue)) {
      return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200';
    }
    if (['inactive', 'out of stock', 'closed', 'terminated', 'closed lost', 'cancelled', 'expired'].includes(lowerValue)) {
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
    if (['low stock', 'under maintenance', 'overdue', 'on leave'].includes(lowerValue)) {
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200';
    }
    if (['pending', 'pending approval', 'draft', 'prospecting', 'qualification'].includes(lowerValue)) {
      return 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200';
    }
    if (['negotiation', 'proposal', 'submitted', 'sent'].includes(lowerValue)) {
      return 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-200';
    }
    if (['discontinued'].includes(lowerValue)) {
      return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200';
    }
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  // Render cell content
  const renderCell = (row: Record<string, unknown>, column: string) => {
    const isEditing = editingCell?.rowId === row.id && editingCell?.column === column;
    const value = row[column];
    const colConfig = columns.find(c => c.key === column);
    const isStatusColumn = column.toLowerCase() === 'status' || column.toLowerCase() === 'stage';

    if (isEditing) {
      return (
        <input
          ref={editInputRef}
          type={typeof value === 'number' ? 'number' : 'text'}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={saveEdit}
          onKeyDown={handleEditKeyDown}
          className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-default)',
            color: 'var(--text-primary)',
          }}
        />
      );
    }

    // Display mode
    if (isStatusColumn && typeof value === 'string') {
      return (
        <span
          onClick={() => colConfig?.editable && startEditing(row.id as string | number, column, value)}
          className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${colConfig?.editable ? 'cursor-pointer hover:opacity-80' : ''} ${getStatusBadgeClass(value)}`}
        >
          {value}
        </span>
      );
    }

    if (typeof value === 'number') {
      return (
        <span
          onClick={() => colConfig?.editable && startEditing(row.id as string | number, column, value)}
          className={`${colConfig?.editable ? 'cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20' : ''} px-1 py-0.5 rounded`}
          style={{ color: 'var(--text-secondary)' }}
        >
          {value.toLocaleString()}
        </span>
      );
    }

    return (
      <span
        onClick={() => colConfig?.editable && startEditing(row.id as string | number, column, value)}
        className={`${colConfig?.editable ? 'cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20' : ''} px-1 py-0.5 rounded`}
        style={{ color: 'var(--text-primary)' }}
      >
        {String(value ?? '')}
      </span>
    );
  };

  // Table list icons
  const getTableIcon = (tableName: string) => {
    const iconMap: Record<string, JSX.Element> = {
      accounts: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      users: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      default: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
        </svg>
      ),
    };
    return iconMap[tableName] || iconMap.default;
  };

  // Render form field
  const renderFormField = (col: ColumnConfig) => {
    const value = formData[col.key] ?? '';
    const isReadOnly = activeModal === 'view' || !col.editable;

    return (
      <div key={col.key} className="mb-4">
        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
          {col.label}
        </label>
        <input
          type={col.type?.includes('int') || col.type?.includes('numeric') ? 'number' : 'text'}
          value={String(value)}
          onChange={(e) => handleFormChange(col.key, e.target.value)}
          readOnly={isReadOnly}
          className={`w-full px-3 py-2 rounded-lg border ${isReadOnly ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
          style={{
            backgroundColor: isReadOnly ? undefined : 'var(--bg-card)',
            borderColor: 'var(--border-default)',
            color: 'var(--text-primary)',
          }}
        />
      </div>
    );
  };

  return (
    <div className="flex gap-6 h-full">
      {/* Left Panel - Table List */}
      <div
        className="w-56 flex-shrink-0 rounded-xl border overflow-hidden"
        style={{
          backgroundColor: 'var(--bg-card)',
          borderColor: 'var(--border-default)',
        }}
      >
        <div
          className="px-4 py-3 border-b"
          style={{ borderColor: 'var(--border-default)' }}
        >
          <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Tables
          </h3>
        </div>
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 250px)' }}>
          {isLoadingTables ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              Loading tables...
            </div>
          ) : tableList.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              No tables found
            </div>
          ) : (
            tableList.map((table) => (
              <button
                key={table.id}
                onClick={() => setSelectedTable(table)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${
                  selectedTable?.id === table.id
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-r-2 border-blue-500'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
                }`}
                style={{
                  color: selectedTable?.id === table.id ? undefined : 'var(--text-secondary)',
                }}
              >
                <span className={selectedTable?.id === table.id ? 'text-blue-500' : 'text-gray-400'}>
                  {getTableIcon(table.name)}
                </span>
                <span className="truncate">{table.label}</span>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right Panel - Data Table */}
      <div className="flex-1 space-y-4 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              {selectedTable?.label || 'Select a Table'}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {processedData.length} records {columns.some(c => c.editable) && '• Click any cell to edit'}
            </p>
          </div>
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Clear Filters ({activeFilterCount})
            </button>
          )}
        </div>

        {/* Action Toolbar */}
        <div
          className="flex items-center gap-1 p-2 rounded-lg border"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-default)',
          }}
        >
          <button
            onClick={handleAddRecord}
            className="flex items-center justify-center p-2 rounded-lg transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20 group"
            title="Add Record"
            style={{ color: 'var(--text-secondary)' }}
          >
            <AddIcon size={20} className="group-hover:text-blue-600 transition-colors" />
          </button>
          <button
            onClick={selectedRows.size === 1 ? handleEditRecord : handleViewRecord}
            className="flex items-center justify-center p-2 rounded-lg transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20 group"
            title={selectedRows.size === 1 ? "View/Edit Record" : "Select one record to view"}
            style={{ color: 'var(--text-secondary)' }}
          >
            <ViewIcon size={20} className="group-hover:text-blue-600 transition-colors" />
          </button>
          <button
            onClick={handleDeleteRecords}
            className="flex items-center justify-center p-2 rounded-lg transition-colors hover:bg-red-50 dark:hover:bg-red-900/20 group"
            title="Delete Selected"
            style={{ color: 'var(--text-secondary)' }}
          >
            <DeleteIcon size={20} className="group-hover:text-red-600 transition-colors" />
          </button>
          <div className="w-px h-6 mx-1" style={{ backgroundColor: 'var(--border-default)' }} />
          <button
            className="flex items-center justify-center p-2 rounded-lg transition-colors hover:bg-green-50 dark:hover:bg-green-900/20 group"
            title="Upload Data"
            style={{ color: 'var(--text-secondary)' }}
            onClick={() => setActiveModal('upload')}
          >
            <UploadIcon size={20} className="group-hover:text-green-600 transition-colors" />
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center justify-center p-2 rounded-lg transition-colors hover:bg-green-50 dark:hover:bg-green-900/20 group"
            title="Download Data"
            style={{ color: 'var(--text-secondary)' }}
          >
            <DownloadIcon size={20} className="group-hover:text-green-600 transition-colors" />
          </button>
        </div>

        {/* Data Table */}
        <div
          className="rounded-xl overflow-hidden border"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-default)',
          }}
        >
          {isLoadingData ? (
            <div className="px-4 py-16 text-center text-sm text-gray-500">
              Loading data...
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-hover)' }}>
                    {/* Checkbox column header */}
                    <th className="px-4 py-3 w-12">
                      <div className="flex items-center justify-center">
                        <input
                          type="checkbox"
                          checked={isAllSelected}
                          ref={(el) => {
                            if (el) el.indeterminate = isSomeSelected;
                          }}
                          onChange={toggleSelectAll}
                          className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          title={isAllSelected ? 'Deselect all' : 'Select all'}
                        />
                      </div>
                    </th>
                    {columns.map((col) => (
                      <th
                        key={col.key}
                        className="px-4 py-3 text-left text-sm font-semibold"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        <div className="space-y-2">
                          {/* Column header with sort */}
                          <div
                            className="flex items-center gap-2 cursor-pointer select-none hover:text-blue-600 transition-colors"
                            onClick={() => handleSort(col.key)}
                          >
                            <span>{col.label}</span>
                            {renderSortIcon(col.key)}
                          </div>

                          {/* Filter dropdown */}
                          <div
                            ref={(el) => (filterRefs.current[col.key] = el)}
                            className="relative"
                          >
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFilterDropdown(col.key);
                              }}
                              className={`flex items-center gap-1 px-2 py-1 text-xs rounded border transition-colors ${
                                columnFilters[col.key]?.values?.length > 0
                                  ? 'bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/30 dark:border-blue-600 dark:text-blue-400'
                                  : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400'
                              }`}
                            >
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                              </svg>
                              <span className="truncate max-w-[80px]">
                                {columnFilters[col.key]?.values?.length > 0
                                  ? `${columnFilters[col.key].values.length} selected`
                                  : 'Filter'}
                              </span>
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </button>

                            {columnFilters[col.key]?.isOpen && (
                              <div
                                className="absolute z-10 mt-1 w-48 rounded-lg shadow-lg border overflow-hidden"
                                style={{
                                  backgroundColor: 'var(--bg-card)',
                                  borderColor: 'var(--border-default)',
                                }}
                              >
                                {/* Select All / Clear */}
                                <div
                                  className="flex items-center justify-between px-3 py-2 border-b text-xs"
                                  style={{ borderColor: 'var(--border-default)' }}
                                >
                                  <button
                                    onClick={() => handleSelectAll(col.key)}
                                    className="text-blue-600 hover:underline"
                                  >
                                    Select All
                                  </button>
                                  <button
                                    onClick={() => handleClearColumn(col.key)}
                                    className="text-gray-500 hover:underline"
                                  >
                                    Clear
                                  </button>
                                </div>
                                <div className="max-h-48 overflow-y-auto">
                                  {getUniqueValues(col.key).map((option) => (
                                    <label
                                      key={option}
                                      className="flex items-center gap-2 px-3 py-2 text-xs hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                                    >
                                      <input
                                        type="checkbox"
                                        checked={columnFilters[col.key]?.values?.includes(option) || false}
                                        onChange={() => handleFilterToggle(col.key, option)}
                                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                      />
                                      <span style={{ color: 'var(--text-primary)' }}>{option}</span>
                                    </label>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {processedData.map((item) => (
                    <tr
                      key={String(item.id)}
                      className={`border-t hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors ${
                        selectedRows.has(item.id as string | number) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                      style={{ borderColor: 'var(--border-default)' }}
                    >
                      {/* Checkbox cell */}
                      <td className="px-4 py-3 w-12">
                        <div className="flex items-center justify-center">
                          <input
                            type="checkbox"
                            checked={selectedRows.has(item.id as string | number)}
                            onChange={() => toggleRowSelection(item.id as string | number)}
                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          />
                        </div>
                      </td>
                      {columns.map((col) => (
                        <td
                          key={col.key}
                          className="px-4 py-3 text-sm"
                        >
                          {renderCell(item, col.key)}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {processedData.length === 0 && (
                    <tr>
                      <td
                        colSpan={columns.length + 1}
                        className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                      >
                        {hasActiveFilters ? 'No data matching the current filters' : 'No data available'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Footer */}
          <div
            className="px-4 py-3 border-t flex items-center justify-between"
            style={{ borderColor: 'var(--border-default)' }}
          >
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {selectedRows.size > 0 && (
                <span className="text-blue-600 dark:text-blue-400 font-medium mr-2">
                  {selectedRows.size} selected
                </span>
              )}
              Showing {processedData.length} of {data.length} results
              {hasActiveFilters && ' (filtered)'}
            </span>
            <div className="flex gap-2">
              <button className="btn btn-outline btn-sm" disabled>
                Previous
              </button>
              <button className="btn btn-outline btn-sm" disabled>
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Add/Edit/View Modal */}
      {(activeModal === 'add' || activeModal === 'edit' || activeModal === 'view') && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setActiveModal(null)}
          />
          <div
            className="relative w-full max-w-2xl max-h-[90vh] overflow-auto m-4 rounded-xl shadow-2xl"
            style={{ backgroundColor: 'var(--bg-page)' }}
          >
            <div
              className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-default)',
              }}
            >
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                {activeModal === 'add' ? 'Add New Record' : activeModal === 'edit' ? 'Edit Record' : 'View Record'}
              </h2>
              <button
                onClick={() => setActiveModal(null)}
                className="p-2 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
                style={{ color: 'var(--text-secondary)' }}
              >
                <CloseIcon size={20} />
              </button>
            </div>
            <div className="p-6">
              {columns.filter(col => !['id', 'created_at', 'updated_at', '_portco_id', '_created_at', '_updated_at'].includes(col.key)).map(renderFormField)}
            </div>
            {activeModal !== 'view' && (
              <div
                className="sticky bottom-0 flex items-center justify-end gap-3 px-6 py-4 border-t"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-default)',
                }}
              >
                <button
                  onClick={() => setActiveModal(null)}
                  className="px-4 py-2 text-sm rounded-lg border hover:bg-gray-50 dark:hover:bg-gray-800"
                  style={{
                    borderColor: 'var(--border-default)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={saveRecord}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {activeModal === 'delete' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setActiveModal(null)}
          />
          <div
            className="relative w-full max-w-md m-4 rounded-xl shadow-2xl"
            style={{ backgroundColor: 'var(--bg-card)' }}
          >
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                Confirm Delete
              </h2>
              <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
                Are you sure you want to delete {selectedRows.size} record(s)? This action cannot be undone.
              </p>
              <div className="flex items-center justify-end gap-3">
                <button
                  onClick={() => setActiveModal(null)}
                  className="px-4 py-2 text-sm rounded-lg border hover:bg-gray-50 dark:hover:bg-gray-800"
                  style={{
                    borderColor: 'var(--border-default)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDelete}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {isSaving ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {activeModal === 'upload' && selectedTable && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setActiveModal(null)}
          />
          <div
            className="relative w-full max-w-7xl max-h-[90vh] overflow-auto m-4 rounded-xl shadow-2xl"
            style={{ backgroundColor: 'var(--bg-page)' }}
          >
            <div
              className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-default)',
              }}
            >
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Upload Data to {selectedTable.label}
              </h2>
              <button
                onClick={() => setActiveModal(null)}
                className="p-2 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
                style={{ color: 'var(--text-secondary)' }}
              >
                <CloseIcon size={20} />
              </button>
            </div>
            <div className="p-6">
              <FileUpload
                portcoId={selectedTable.name}
                onUploadComplete={() => {
                  fetchTableData(selectedTable.name);
                  setActiveModal(null);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataPage;
