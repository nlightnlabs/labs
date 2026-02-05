// Export all data types
export type { Account } from './accounts';
export type { Opportunity } from './opportunities';
export type { Contact } from './contacts';
export type { PurchaseOrder } from './purchaseOrders';
export type { Invoice } from './invoices';
export type { Facility } from './facilities';
export type { InventoryItem } from './inventory';
export type { Supplier } from './suppliers';
export type { Contract } from './contracts';
export type { Employee } from './employees';

// Import all data and columns
import { accounts, accountColumns } from './accounts';
import { opportunities, opportunityColumns } from './opportunities';
import { contacts, contactColumns } from './contacts';
import { purchaseOrders, purchaseOrderColumns } from './purchaseOrders';
import { invoices, invoiceColumns } from './invoices';
import { facilities, facilityColumns } from './facilities';
import { inventory, inventoryColumns } from './inventory';
import { suppliers, supplierColumns } from './suppliers';
import { contracts, contractColumns } from './contracts';
import { employees, employeeColumns } from './employees';

// Table configuration type
export interface TableConfig {
  id: string;
  name: string;
  label: string;
  icon?: string;
}

// Column configuration type
export interface ColumnConfig {
  key: string;
  label: string;
  editable: boolean;
}

// Available tables list
export const tableList: TableConfig[] = [
  { id: 'accounts', name: 'accounts', label: 'Accounts' },
  { id: 'opportunities', name: 'opportunities', label: 'Opportunities' },
  { id: 'contacts', name: 'contacts', label: 'Contacts' },
  { id: 'purchase_orders', name: 'purchase_orders', label: 'Purchase Orders' },
  { id: 'invoices', name: 'invoices', label: 'Invoices' },
  { id: 'facilities', name: 'facilities', label: 'Facilities' },
  { id: 'inventory', name: 'inventory', label: 'Inventory' },
  { id: 'suppliers', name: 'suppliers', label: 'Suppliers' },
  { id: 'contracts', name: 'contracts', label: 'Contracts' },
  { id: 'employees', name: 'employees', label: 'Employees' },
];

// Data registry mapping table names to data
const dataRegistry: Record<string, any[]> = {
  accounts,
  opportunities,
  contacts,
  purchase_orders: purchaseOrders,
  invoices,
  facilities,
  inventory,
  suppliers,
  contracts,
  employees,
};

// Columns registry mapping table names to column configs
const columnsRegistry: Record<string, ColumnConfig[]> = {
  accounts: accountColumns,
  opportunities: opportunityColumns,
  contacts: contactColumns,
  purchase_orders: purchaseOrderColumns,
  invoices: invoiceColumns,
  facilities: facilityColumns,
  inventory: inventoryColumns,
  suppliers: supplierColumns,
  contracts: contractColumns,
  employees: employeeColumns,
};

// Dynamic data loader function
export function getTableData(tableName: string): any[] {
  const normalizedName = tableName.toLowerCase().replace(/\s+/g, '_');
  return dataRegistry[normalizedName] || [];
}

// Dynamic columns loader function
export function getTableColumns(tableName: string): ColumnConfig[] {
  const normalizedName = tableName.toLowerCase().replace(/\s+/g, '_');
  return columnsRegistry[normalizedName] || [];
}

// Get table config by name
export function getTableConfig(tableName: string): TableConfig | undefined {
  const normalizedName = tableName.toLowerCase().replace(/\s+/g, '_');
  return tableList.find(t => t.name === normalizedName || t.id === normalizedName);
}

// Export all data sets directly for convenience
export {
  accounts,
  opportunities,
  contacts,
  purchaseOrders,
  invoices,
  facilities,
  inventory,
  suppliers,
  contracts,
  employees,
};
