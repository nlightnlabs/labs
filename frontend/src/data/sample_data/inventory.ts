export interface InventoryItem {
  id: number;
  sku: string;
  name: string;
  category: string;
  quantity: number;
  reorderLevel: number;
  unitCost: string;
  location: string;
  status: 'In Stock' | 'Low Stock' | 'Out of Stock' | 'Discontinued';
}

export const inventory: InventoryItem[] = [
  { id: 1, sku: 'SKU-001', name: 'Widget Pro X', category: 'Electronics', quantity: 1250, reorderLevel: 200, unitCost: '$45.00', location: 'Warehouse A', status: 'In Stock' },
  { id: 2, sku: 'SKU-002', name: 'Steel Brackets', category: 'Hardware', quantity: 5400, reorderLevel: 1000, unitCost: '$2.50', location: 'Warehouse B', status: 'In Stock' },
  { id: 3, sku: 'SKU-003', name: 'Office Chair Deluxe', category: 'Furniture', quantity: 85, reorderLevel: 100, unitCost: '$189.00', location: 'Warehouse A', status: 'Low Stock' },
  { id: 4, sku: 'SKU-004', name: 'LED Display Panel', category: 'Electronics', quantity: 320, reorderLevel: 50, unitCost: '$275.00', location: 'Warehouse C', status: 'In Stock' },
  { id: 5, sku: 'SKU-005', name: 'Copper Wire Spool', category: 'Raw Materials', quantity: 0, reorderLevel: 500, unitCost: '$120.00', location: 'Warehouse B', status: 'Out of Stock' },
  { id: 6, sku: 'SKU-006', name: 'Safety Helmets', category: 'Safety', quantity: 890, reorderLevel: 200, unitCost: '$35.00', location: 'Warehouse A', status: 'In Stock' },
  { id: 7, sku: 'SKU-007', name: 'Packaging Boxes (Large)', category: 'Packaging', quantity: 12500, reorderLevel: 5000, unitCost: '$1.25', location: 'Warehouse D', status: 'In Stock' },
  { id: 8, sku: 'SKU-008', name: 'Hydraulic Pump', category: 'Machinery', quantity: 45, reorderLevel: 30, unitCost: '$850.00', location: 'Warehouse C', status: 'Low Stock' },
  { id: 9, sku: 'SKU-009', name: 'Vintage Monitor 17"', category: 'Electronics', quantity: 12, reorderLevel: 0, unitCost: '$150.00', location: 'Warehouse A', status: 'Discontinued' },
  { id: 10, sku: 'SKU-010', name: 'Industrial Lubricant', category: 'Chemicals', quantity: 780, reorderLevel: 200, unitCost: '$28.00', location: 'Warehouse B', status: 'In Stock' },
];

export const inventoryColumns = [
  { key: 'sku' as const, label: 'SKU', editable: false },
  { key: 'name' as const, label: 'Item Name', editable: true },
  { key: 'category' as const, label: 'Category', editable: true },
  { key: 'quantity' as const, label: 'Qty', editable: true },
  { key: 'unitCost' as const, label: 'Unit Cost', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
