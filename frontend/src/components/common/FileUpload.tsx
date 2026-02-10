import React, { useState } from 'react';
import { Card, Button } from '@/components/common';
import * as XLSX from 'xlsx';
import { s3Api, tablesApi } from '@/services/api';

// Standard taxonomy fields for mapping
const STANDARD_TAXONOMY_FIELDS = [
  { id: 'customer_id', label: 'Customer ID', category: 'Customer' },
  { id: 'customer_name', label: 'Customer Name', category: 'Customer' },
  { id: 'customer_email', label: 'Customer Email', category: 'Customer' },
  { id: 'customer_phone', label: 'Customer Phone', category: 'Customer' },
  { id: 'customer_address', label: 'Customer Address', category: 'Customer' },
  { id: 'product_id', label: 'Product ID', category: 'Product' },
  { id: 'product_name', label: 'Product Name', category: 'Product' },
  { id: 'product_sku', label: 'Product SKU', category: 'Product' },
  { id: 'product_category', label: 'Product Category', category: 'Product' },
  { id: 'product_price', label: 'Product Price', category: 'Product' },
  { id: 'order_id', label: 'Order ID', category: 'Transaction' },
  { id: 'order_date', label: 'Order Date', category: 'Transaction' },
  { id: 'order_amount', label: 'Order Amount', category: 'Transaction' },
  { id: 'quantity', label: 'Quantity', category: 'Transaction' },
  { id: 'unit_price', label: 'Unit Price', category: 'Transaction' },
  { id: 'discount', label: 'Discount', category: 'Transaction' },
  { id: 'tax', label: 'Tax', category: 'Transaction' },
  { id: 'total', label: 'Total', category: 'Transaction' },
  { id: 'invoice_id', label: 'Invoice ID', category: 'Finance' },
  { id: 'invoice_date', label: 'Invoice Date', category: 'Finance' },
  { id: 'payment_date', label: 'Payment Date', category: 'Finance' },
  { id: 'payment_method', label: 'Payment Method', category: 'Finance' },
  { id: 'account_number', label: 'Account Number', category: 'Finance' },
  { id: 'gl_code', label: 'GL Code', category: 'Finance' },
  { id: 'cost_center', label: 'Cost Center', category: 'Finance' },
  { id: 'department', label: 'Department', category: 'Organization' },
  { id: 'region', label: 'Region', category: 'Organization' },
  { id: 'country', label: 'Country', category: 'Organization' },
  { id: 'vendor_id', label: 'Vendor ID', category: 'Vendor' },
  { id: 'vendor_name', label: 'Vendor Name', category: 'Vendor' },
  { id: 'employee_id', label: 'Employee ID', category: 'HR' },
  { id: 'employee_name', label: 'Employee Name', category: 'HR' },
  { id: 'date', label: 'Date', category: 'General' },
  { id: 'description', label: 'Description', category: 'General' },
  { id: 'notes', label: 'Notes', category: 'General' },
  { id: 'status', label: 'Status', category: 'General' },
  { id: 'type', label: 'Type', category: 'General' },
];

// Data types for column mapping
const DATA_TYPES = [
  { id: 'string', label: 'Text' },
  { id: 'integer', label: 'Integer' },
  { id: 'decimal', label: 'Decimal' },
  { id: 'date', label: 'Date' },
  { id: 'datetime', label: 'Date/Time' },
  { id: 'boolean', label: 'Boolean' },
  { id: 'currency', label: 'Currency' },
  { id: 'percentage', label: 'Percentage' },
  { id: 'email', label: 'Email' },
  { id: 'phone', label: 'Phone' },
  { id: 'url', label: 'URL' },
  { id: 'jsonb', label: 'JSON' },
];

// Business categories for dataset classification
const BUSINESS_CATEGORIES = [
  { id: 'sales', label: 'Sales' },
  { id: 'marketing', label: 'Marketing' },
  { id: 'finance', label: 'Finance' },
  { id: 'procurement', label: 'Procurement' },
  { id: 'facilities', label: 'Facilities' },
  { id: 'it', label: 'IT' },
  { id: 'legal', label: 'Legal' },
  { id: 'hr', label: 'HR' },
  { id: 'customer_support', label: 'Customer Support' },
  { id: 'operations', label: 'Operations' },
  { id: 'inventory', label: 'Inventory' },
  { id: 'logistics', label: 'Logistics' },
  { id: 'accounting', label: 'Accounting' },
  { id: 'compliance', label: 'Compliance' },
];

// Represents a parsed file with its data
interface ParsedFile {
  id: string;
  name: string;
  size: number;
  type: 'csv' | 'xlsx';
  headers: string[];
  rows: string[][];
  uploadedAt: Date;
  rawFile: File;
}

interface FieldMapping {
  originalField: string;
  mappedField: string;
  label: string;
  dataType: string;
  description: string;
}

interface FileUploadProps {
  portcoId: string;
  onUploadComplete?: () => void;
}

type DetailTab = 'preview' | 'configure' | 'save';

export const FileUpload: React.FC<FileUploadProps> = ({ portcoId, onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<ParsedFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Tab state for the detail panel
  const [activeDetailTab, setActiveDetailTab] = useState<DetailTab>('preview');

  // Field mappings per file
  const [fieldMappings, setFieldMappings] = useState<Record<string, FieldMapping[]>>({});

  // Metadata form state
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  // Save state
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveResult, setSaveResult] = useState<{
    tableName?: string;
    rowCount?: number;
    columnCount?: number;
    tableCreated?: boolean;
  } | null>(null);

  // Get the currently selected file
  const selectedFile = uploadedFiles.find(f => f.id === selectedFileId);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    handleFilesSelect(files);
  };

  const validateFile = (file: File): string | null => {
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ];

    if (!validTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      return `Invalid file type: ${file.name}. Please upload CSV or XLSX files.`;
    }

    if (file.size > 100 * 1024 * 1024) {
      return `File too large: ${file.name}. Maximum size is 100MB.`;
    }

    return null;
  };

  // Parse CSV content
  const parseCSV = (content: string): { headers: string[]; rows: string[][] } => {
    const lines = content.split(/\r?\n/).filter(line => line.trim());
    if (lines.length === 0) {
      return { headers: [], rows: [] };
    }

    // Simple CSV parser that handles quoted fields
    const parseLine = (line: string): string[] => {
      const result: string[] = [];
      let current = '';
      let inQuotes = false;

      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          if (inQuotes && line[i + 1] === '"') {
            current += '"';
            i++;
          } else {
            inQuotes = !inQuotes;
          }
        } else if (char === ',' && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim());
      return result;
    };

    const headers = parseLine(lines[0]);
    const rows = lines.slice(1).map(line => parseLine(line));

    return { headers, rows };
  };

  // Parse XLSX content
  const parseXLSX = (arrayBuffer: ArrayBuffer): { headers: string[]; rows: string[][] } => {
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];

    // Convert to array of arrays
    const data: string[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

    if (data.length === 0) {
      return { headers: [], rows: [] };
    }

    const headers = data[0].map(h => String(h));
    const rows = data.slice(1).map(row => row.map(cell => String(cell)));

    return { headers, rows };
  };

  // Sanitize field name for database column naming
  const sanitizeFieldName = (fieldName: string): string => {
    return fieldName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')  // Replace non-alphanumeric with underscore
      .replace(/^_+|_+$/g, '')       // Trim leading/trailing underscores
      .replace(/_+/g, '_');          // Collapse multiple underscores
  };

  // Convert snake_case to Title Case for UI labels
  const snakeToTitleCase = (snakeStr: string): string => {
    return snakeStr
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Get label for a mapped field (from taxonomy or generate from snake_case)
  const getLabelForMappedField = (mappedField: string): string => {
    const taxonomyField = STANDARD_TAXONOMY_FIELDS.find(f => f.id === mappedField);
    if (taxonomyField) {
      return taxonomyField.label;
    }
    return snakeToTitleCase(mappedField);
  };

  // Guess field mapping based on field name
  const guessFieldMapping = (fieldName: string): string => {
    const lowerField = fieldName.toLowerCase().replace(/[_\-\s]/g, '');

    const mappings: Record<string, string> = {
      'customerid': 'customer_id',
      'custid': 'customer_id',
      'customername': 'customer_name',
      'custname': 'customer_name',
      'name': 'customer_name',
      'email': 'customer_email',
      'emailaddress': 'customer_email',
      'phone': 'customer_phone',
      'phonenumber': 'customer_phone',
      'address': 'customer_address',
      'productid': 'product_id',
      'prodid': 'product_id',
      'productname': 'product_name',
      'prodname': 'product_name',
      'sku': 'product_sku',
      'category': 'product_category',
      'price': 'product_price',
      'unitprice': 'unit_price',
      'orderid': 'order_id',
      'orderno': 'order_id',
      'orderdate': 'order_date',
      'orderamount': 'order_amount',
      'amount': 'order_amount',
      'qty': 'quantity',
      'quantity': 'quantity',
      'discount': 'discount',
      'tax': 'tax',
      'total': 'total',
      'invoiceid': 'invoice_id',
      'invoicedate': 'invoice_date',
      'paymentdate': 'payment_date',
      'paymentmethod': 'payment_method',
      'accountnumber': 'account_number',
      'accountno': 'account_number',
      'glcode': 'gl_code',
      'costcenter': 'cost_center',
      'department': 'department',
      'dept': 'department',
      'region': 'region',
      'country': 'country',
      'vendorid': 'vendor_id',
      'vendorname': 'vendor_name',
      'employeeid': 'employee_id',
      'empid': 'employee_id',
      'employeename': 'employee_name',
      'date': 'date',
      'asofdate': 'date',
      'description': 'description',
      'desc': 'description',
      'notes': 'notes',
      'status': 'status',
      'type': 'type',
      'accounttype': 'type',
      'accountname': 'description',
      'debit': 'order_amount',
      'credit': 'order_amount',
      'location': 'region',
    };

    // If no taxonomy match, use the sanitized original field name
    return mappings[lowerField] || sanitizeFieldName(fieldName);
  };

  // Guess data type based on field name and sample data
  const guessDataType = (fieldName: string, rows: string[][]): string => {
    const lowerField = fieldName.toLowerCase();

    if (lowerField.includes('date') || lowerField.includes('time')) {
      return lowerField.includes('time') ? 'datetime' : 'date';
    }
    if (lowerField.includes('email')) return 'email';
    if (lowerField.includes('phone') || lowerField.includes('tel')) return 'phone';
    if (lowerField.includes('url') || lowerField.includes('website')) return 'url';
    if (lowerField.includes('price') || lowerField.includes('amount') || lowerField.includes('cost') || lowerField.includes('total') || lowerField.includes('debit') || lowerField.includes('credit')) return 'currency';
    if (lowerField.includes('percent') || lowerField.includes('rate')) return 'percentage';
    if (lowerField.includes('qty') || lowerField.includes('quantity') || lowerField.includes('count')) return 'integer';
    if (lowerField.includes('id') && !lowerField.includes('email')) return 'string';

    // Analyze sample data
    const headerIndex = rows.length > 0 ? rows[0].findIndex((_, i) => i === rows[0].indexOf(fieldName)) : -1;
    if (headerIndex >= 0) {
      const sampleValues = rows.slice(0, 5).map(row => row[headerIndex]).filter(v => v);

      const allNumbers = sampleValues.every(v => !isNaN(Number(v)));
      if (allNumbers && sampleValues.length > 0) {
        const hasDecimals = sampleValues.some(v => v.includes('.'));
        return hasDecimals ? 'decimal' : 'integer';
      }

      const datePattern = /^\d{4}-\d{2}-\d{2}/;
      if (sampleValues.every(v => datePattern.test(v))) {
        return 'date';
      }
    }

    return 'string';
  };

  const processFile = async (file: File): Promise<ParsedFile> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      const isCSV = file.name.toLowerCase().endsWith('.csv');

      reader.onload = (e) => {
        try {
          let parsed: { headers: string[]; rows: string[][] };

          if (isCSV) {
            const content = e.target?.result as string;
            parsed = parseCSV(content);
          } else {
            const arrayBuffer = e.target?.result as ArrayBuffer;
            parsed = parseXLSX(arrayBuffer);
          }

          resolve({
            id: `file-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`,
            name: file.name,
            size: file.size,
            type: isCSV ? 'csv' : 'xlsx',
            headers: parsed.headers,
            rows: parsed.rows,
            uploadedAt: new Date(),
            rawFile: file,
          });
        } catch (error) {
          reject(new Error(`Failed to parse ${file.name}: ${error}`));
        }
      };

      reader.onerror = () => reject(new Error(`Failed to read ${file.name}`));

      if (isCSV) {
        reader.readAsText(file);
      } else {
        reader.readAsArrayBuffer(file);
      }
    });
  };

  const handleFilesSelect = async (files: File[]) => {
    setUploadError(null);
    const errors: string[] = [];
    const validFiles: File[] = [];

    files.forEach((file) => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      setUploadError(errors.join(' '));
    }

    if (validFiles.length === 0) return;

    setIsProcessing(true);

    try {
      const parsedFiles = await Promise.all(validFiles.map(processFile));

      // Initialize field mappings for each new file
      parsedFiles.forEach(pf => {
        const initialMappings = pf.headers.map((header, index) => {
          const mappedField = guessFieldMapping(header);
          return {
            originalField: header,
            mappedField,
            label: getLabelForMappedField(mappedField),
            dataType: guessDataType(header, pf.rows.map(r => r[index] ? [r[index]] : []).flat().map(v => [v])),
            description: '',
          };
        });
        setFieldMappings(prev => ({ ...prev, [pf.id]: initialMappings }));
      });

      setUploadedFiles(prev => [...prev, ...parsedFiles]);

      // Auto-select the first newly uploaded file
      if (parsedFiles.length > 0 && !selectedFileId) {
        setSelectedFileId(parsedFiles[0].id);
        // Pre-populate dataset name
        const baseName = parsedFiles[0].name.replace(/\.[^/.]+$/, '');
        setDatasetName(baseName);
      }
    } catch (error) {
      setUploadError(String(error));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFilesSelect(Array.from(files));
    }
    e.target.value = '';
  };

  const handleDeleteFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    if (selectedFileId === fileId) {
      setSelectedFileId(null);
      setActiveDetailTab('preview');
    }
    // Clean up field mappings
    setFieldMappings(prev => {
      const newMappings = { ...prev };
      delete newMappings[fileId];
      return newMappings;
    });
  };

  const handleSelectFile = (fileId: string) => {
    const file = uploadedFiles.find(f => f.id === fileId);
    setSelectedFileId(fileId);
    setActiveDetailTab('preview');
    setSaveSuccess(false);
    setSaveError(null);
    setSaveResult(null);
    // Pre-populate dataset name when selecting a file
    if (file) {
      const baseName = file.name.replace(/\.[^/.]+$/, '');
      setDatasetName(baseName);
      setDatasetDescription('');
      setSelectedCategories([]);
    }
  };

  const updateFieldMapping = (fileId: string, index: number, updates: Partial<FieldMapping>) => {
    setFieldMappings(prev => ({
      ...prev,
      [fileId]: prev[fileId].map((mapping, i) =>
        i === index ? { ...mapping, ...updates } : mapping
      ),
    }));
  };

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(c => c !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleSave = async () => {
    if (!selectedFile || !datasetName.trim()) return;

    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    const tableName = datasetName
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[^a-z0-9_]/g, '');

    // Build column mappings for database table creation (original header -> mapped field name)
    const currentFileMappings = fieldMappings[selectedFile.id] || [];
    const columnMappings: Record<string, string> = {};
    currentFileMappings.forEach(mapping => {
      columnMappings[mapping.originalField] = mapping.mappedField;
    });

    // Transform file data to records using mapped field names
    const records = selectedFile.rows.map(row => {
      const record: Record<string, unknown> = {};
      selectedFile.headers.forEach((header, index) => {
        const mappedField = columnMappings[header] || header;
        record[mappedField] = row[index] || null;
      });
      return record;
    });

    const metadata = {
      name: datasetName,
      description: datasetDescription,
      categories: selectedCategories,
      field_mappings: currentFileMappings,
      column_mappings: columnMappings,
      original_filename: selectedFile.name,
      row_count: selectedFile.rows.length,
      column_count: selectedFile.headers.length,
      created_at: new Date().toISOString(),
    };

    try {
      // Save metadata to S3
      await s3Api.saveData(
        `datasets/${portcoId}`,
        `${tableName}_metadata.json`,
        metadata
      );

      // Insert records into database table
      const response = await tablesApi.createRecords(
        tableName,
        records,
        'data',
        undefined,
        // Build data model from field mappings
        currentFileMappings.reduce((acc, mapping) => {
          acc[mapping.mappedField] = mapping.dataType;
          return acc;
        }, {} as Record<string, unknown>)
      );

      const responseData = response.data as { success?: boolean; error?: string; data?: unknown[] };

      if (responseData.success !== false && !responseData.error) {
        setSaveSuccess(true);
        setSaveResult({
          tableName: tableName,
          rowCount: records.length,
          columnCount: selectedFile.headers.length,
          tableCreated: true,
        });
        onUploadComplete?.();
      } else {
        setSaveError(responseData.error || 'Failed to save dataset');
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      setSaveError(err.response?.data?.detail || 'Failed to save dataset');
      console.error('Failed to save dataset:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleString();
  };

  const currentMappings = selectedFileId ? fieldMappings[selectedFileId] || [] : [];

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card className={uploadedFiles.length > 0 ? "p-4" : "p-5"}>
        {/* Error Message */}
        {uploadError && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-600 dark:text-red-400">{uploadError}</p>
          </div>
        )}

        {/* Drop Zone - Compact when files exist, Full when empty */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl transition-colors ${
            isDragging
              ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/20'
              : 'border-gray-300 dark:border-gray-700 hover:border-teal-400'
          } ${uploadedFiles.length > 0 ? 'p-3' : 'p-8 text-center'}`}
        >
          {isProcessing ? (
            <div className={`flex items-center ${uploadedFiles.length > 0 ? 'justify-center gap-3' : 'flex-col'}`}>
              <svg className={`animate-spin text-teal-600 ${uploadedFiles.length > 0 ? 'h-5 w-5' : 'h-10 w-10 mb-4'}`} fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className={`font-medium ${uploadedFiles.length > 0 ? 'text-sm' : 'text-lg'}`} style={{ color: 'var(--text-primary)' }}>
                Processing files...
              </p>
            </div>
          ) : uploadedFiles.length > 0 ? (
            /* Compact drop zone when files exist */
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Drop more files here or
                </p>
              </div>
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleInputChange}
                className="hidden"
                id="file-upload"
                multiple
              />
              <Button
                variant="outline"
                type="button"
                size="sm"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                Browse Files
              </Button>
            </div>
          ) : (
            /* Full drop zone when no files */
            <>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center">
                <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-lg font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Drag and drop your files here
              </p>
              <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
                or click to browse your files (multiple files supported)
              </p>
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleInputChange}
                className="hidden"
                id="file-upload-empty"
                multiple
              />
              <Button
                variant="outline"
                type="button"
                onClick={() => document.getElementById('file-upload-empty')?.click()}
              >
                Browse Files
              </Button>
              <p className="text-xs mt-4" style={{ color: 'var(--text-tertiary)' }}>
                Supported formats: CSV, XLSX (max 100MB per file)
              </p>
            </>
          )}
        </div>
      </Card>

      {/* Uploaded Files List and Preview */}
      {uploadedFiles.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Files List */}
          <Card className="p-5 lg:col-span-1">
            <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Uploaded Files ({uploadedFiles.length})
            </h3>
            <div className="space-y-2">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  onClick={() => handleSelectFile(file.id)}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedFileId === file.id
                      ? 'bg-teal-50 dark:bg-teal-900/20 border border-teal-500'
                      : 'border border-transparent hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    file.type === 'xlsx' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                      {file.name}
                    </p>
                    <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-tertiary)' }}>
                      <span>{formatFileSize(file.size)}</span>
                      <span>-</span>
                      <span>{file.rows.length.toLocaleString()} rows</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteFile(file.id);
                    }}
                    className="p-1 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 flex-shrink-0"
                    title="Delete file"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </Card>

          {/* Data Preview / Configure / Save */}
          <Card className="p-5 lg:col-span-2">
            {selectedFile ? (
              <>
                {/* Header */}
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {selectedFile.name}
                    </h3>
                    <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
                      {selectedFile.headers.length} columns - {selectedFile.rows.length.toLocaleString()} rows - Uploaded {formatDate(selectedFile.uploadedAt)}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${
                    selectedFile.type === 'xlsx'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  }`}>
                    {selectedFile.type}
                  </span>
                </div>

                {/* Tabs */}
                <div className="flex border-b mb-4" style={{ borderColor: 'var(--border-default)' }}>
                  {[
                    { id: 'preview' as DetailTab, label: 'Preview' },
                    { id: 'configure' as DetailTab, label: 'Configure' },
                    { id: 'save' as DetailTab, label: 'Save' },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveDetailTab(tab.id)}
                      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        activeDetailTab === tab.id
                          ? 'border-teal-600 text-teal-600'
                          : 'border-transparent hover:border-gray-300'
                      }`}
                      style={{ color: activeDetailTab === tab.id ? undefined : 'var(--text-secondary)' }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Preview Tab */}
                {activeDetailTab === 'preview' && (
                  <div className="overflow-auto max-h-[500px] border rounded-lg" style={{ borderColor: 'var(--border-default)' }}>
                    <table className="w-full text-sm">
                      <thead className="sticky top-0" style={{ backgroundColor: 'var(--bg-card)' }}>
                        <tr>
                          <th className="px-3 py-2 text-left font-semibold border-b text-xs" style={{ borderColor: 'var(--border-default)', color: 'var(--text-tertiary)' }}>
                            #
                          </th>
                          {selectedFile.headers.map((header, i) => (
                            <th
                              key={i}
                              className="px-3 py-2 text-left font-semibold border-b whitespace-nowrap"
                              style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                            >
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {selectedFile.rows.slice(0, 100).map((row, rowIndex) => (
                          <tr key={rowIndex} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                            <td className="px-3 py-2 border-b text-xs" style={{ borderColor: 'var(--border-default)', color: 'var(--text-tertiary)' }}>
                              {rowIndex + 1}
                            </td>
                            {row.map((cell, cellIndex) => (
                              <td
                                key={cellIndex}
                                className="px-3 py-2 border-b whitespace-nowrap max-w-[200px] truncate"
                                style={{ borderColor: 'var(--border-default)', color: 'var(--text-secondary)' }}
                                title={cell}
                              >
                                {cell || <span className="text-gray-400 italic">empty</span>}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {selectedFile.rows.length > 100 && (
                      <div className="p-3 text-center text-sm border-t" style={{ borderColor: 'var(--border-default)', color: 'var(--text-tertiary)' }}>
                        Showing first 100 of {selectedFile.rows.length.toLocaleString()} rows
                      </div>
                    )}
                  </div>
                )}

                {/* Configure Tab */}
                {activeDetailTab === 'configure' && (
                  <div className="space-y-4">
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Map each column to a standard field and specify its data type.
                    </p>

                    <div className="overflow-auto max-h-[450px]">
                      {/* Header row */}
                      <div className="grid grid-cols-12 gap-3 px-3 py-2 text-xs font-semibold uppercase sticky top-0" style={{ color: 'var(--text-tertiary)', backgroundColor: 'var(--bg-card)' }}>
                        <div className="col-span-2">Original Field</div>
                        <div className="col-span-2">Map To</div>
                        <div className="col-span-2">Label</div>
                        <div className="col-span-2">Data Type</div>
                        <div className="col-span-4">Description</div>
                      </div>

                      <div className="space-y-2">
                        {currentMappings.map((mapping, index) => (
                          <div
                            key={index}
                            className="grid grid-cols-12 gap-3 p-3 rounded-lg border"
                            style={{ borderColor: 'var(--border-default)' }}
                          >
                            {/* Original field name */}
                            <div className="col-span-2 flex items-center">
                              <span className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }} title={mapping.originalField}>
                                {mapping.originalField}
                              </span>
                            </div>

                            {/* Taxonomy field dropdown */}
                            <div className="col-span-2">
                              <select
                                value={mapping.mappedField}
                                onChange={(e) => {
                                  const newMappedField = e.target.value;
                                  const newLabel = getLabelForMappedField(newMappedField);
                                  updateFieldMapping(selectedFile.id, index, {
                                    mappedField: newMappedField,
                                    label: newLabel
                                  });
                                }}
                                className="w-full text-sm px-2 py-1.5 rounded border bg-white dark:bg-gray-800"
                                style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                              >
                                {/* Include the current mapped value if it's from the original field (not in taxonomy) */}
                                {!STANDARD_TAXONOMY_FIELDS.some(f => f.id === mapping.mappedField) && (
                                  <option value={mapping.mappedField}>
                                    {mapping.mappedField} (Original)
                                  </option>
                                )}
                                {Object.entries(
                                  STANDARD_TAXONOMY_FIELDS.reduce((acc, field) => {
                                    if (!acc[field.category]) acc[field.category] = [];
                                    acc[field.category].push(field);
                                    return acc;
                                  }, {} as Record<string, typeof STANDARD_TAXONOMY_FIELDS>)
                                ).map(([category, fields]) => (
                                  <optgroup key={category} label={category}>
                                    {fields.map((field) => (
                                      <option key={field.id} value={field.id}>
                                        {field.label}
                                      </option>
                                    ))}
                                  </optgroup>
                                ))}
                              </select>
                            </div>

                            {/* Label input */}
                            <div className="col-span-2">
                              <input
                                type="text"
                                value={mapping.label}
                                onChange={(e) => updateFieldMapping(selectedFile.id, index, { label: e.target.value })}
                                placeholder="UI Label..."
                                className="w-full text-sm px-2 py-1.5 rounded border bg-white dark:bg-gray-800"
                                style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                              />
                            </div>

                            {/* Data type dropdown */}
                            <div className="col-span-2">
                              <select
                                value={mapping.dataType}
                                onChange={(e) => updateFieldMapping(selectedFile.id, index, { dataType: e.target.value })}
                                className="w-full text-sm px-2 py-1.5 rounded border bg-white dark:bg-gray-800"
                                style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                              >
                                {DATA_TYPES.map((type) => (
                                  <option key={type.id} value={type.id}>
                                    {type.label}
                                  </option>
                                ))}
                              </select>
                            </div>

                            {/* Description input */}
                            <div className="col-span-4">
                              <input
                                type="text"
                                value={mapping.description}
                                onChange={(e) => updateFieldMapping(selectedFile.id, index, { description: e.target.value })}
                                placeholder="Description..."
                                className="w-full text-sm px-2 py-1.5 rounded border bg-white dark:bg-gray-800"
                                style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex justify-end pt-2">
                      <Button
                        onClick={() => setActiveDetailTab('save')}
                        className="bg-teal-600 hover:bg-teal-700 text-white"
                      >
                        Continue to Save
                      </Button>
                    </div>
                  </div>
                )}

                {/* Save Tab */}
                {activeDetailTab === 'save' && (
                  <div className="space-y-6">
                    {/* Success Message */}
                    {saveSuccess && (
                      <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                            Dataset saved successfully!
                          </p>
                        </div>
                        {saveResult?.tableCreated && (
                          <div className="ml-7 text-sm text-green-600 dark:text-green-400">
                            <p>Database table created: <span className="font-mono">{saveResult.tableName}</span></p>
                            <p>{saveResult.rowCount?.toLocaleString()} rows, {saveResult.columnCount} columns</p>
                          </div>
                        )}
                        {saveResult && !saveResult.tableCreated && (
                          <div className="ml-7 text-sm text-amber-600 dark:text-amber-400">
                            <p>Note: Database table creation is pending.</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Error Message */}
                    {saveError && (
                      <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                        <p className="text-sm text-red-600 dark:text-red-400">{saveError}</p>
                      </div>
                    )}

                    {/* Dataset Name */}
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                        Dataset Name *
                      </label>
                      <input
                        type="text"
                        value={datasetName}
                        onChange={(e) => setDatasetName(e.target.value)}
                        placeholder="Enter a name for this dataset"
                        className="w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-800"
                        style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                      />
                      {datasetName && (
                        <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                          S3 path: portco/{portcoId}/{datasetName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}/
                        </p>
                      )}
                    </div>

                    {/* Dataset Description */}
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                        Description
                      </label>
                      <textarea
                        value={datasetDescription}
                        onChange={(e) => setDatasetDescription(e.target.value)}
                        placeholder="Describe what this dataset contains..."
                        rows={3}
                        className="w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-800"
                        style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
                      />
                    </div>

                    {/* Business Categories */}
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                        Business Categories
                      </label>
                      <p className="text-xs mb-3" style={{ color: 'var(--text-tertiary)' }}>
                        Select all categories that apply to this dataset
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {BUSINESS_CATEGORIES.map((category) => (
                          <button
                            key={category.id}
                            onClick={() => toggleCategory(category.id)}
                            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                              selectedCategories.includes(category.id)
                                ? 'bg-teal-100 dark:bg-teal-900/30 border-teal-500 text-teal-700 dark:text-teal-300'
                                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                            }`}
                            style={{ color: selectedCategories.includes(category.id) ? undefined : 'var(--text-secondary)' }}
                          >
                            {category.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Summary */}
                    <div className="p-4 rounded-lg border" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--bg-secondary)' }}>
                      <h4 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Summary</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div style={{ color: 'var(--text-secondary)' }}>File:</div>
                        <div style={{ color: 'var(--text-primary)' }}>{selectedFile.name}</div>
                        <div style={{ color: 'var(--text-secondary)' }}>Rows:</div>
                        <div style={{ color: 'var(--text-primary)' }}>{selectedFile.rows.length.toLocaleString()}</div>
                        <div style={{ color: 'var(--text-secondary)' }}>Columns:</div>
                        <div style={{ color: 'var(--text-primary)' }}>{selectedFile.headers.length}</div>
                        <div style={{ color: 'var(--text-secondary)' }}>Mapped Fields:</div>
                        <div style={{ color: 'var(--text-primary)' }}>{currentMappings.length}</div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-end gap-3 pt-2">
                      <Button
                        variant="outline"
                        onClick={() => setActiveDetailTab('configure')}
                      >
                        Back to Configure
                      </Button>
                      <Button
                        onClick={handleSave}
                        disabled={!datasetName.trim() || isSaving}
                        className="bg-teal-600 hover:bg-teal-700 text-white"
                      >
                        {isSaving ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Saving...
                          </>
                        ) : (
                          'Save'
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-64">
                <svg className="w-12 h-12 mb-4" style={{ color: 'var(--text-tertiary)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p style={{ color: 'var(--text-tertiary)' }}>
                  Select a file to view its contents
                </p>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
