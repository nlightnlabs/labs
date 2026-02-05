export interface PurchaseOrder {
  id: number;
  poNumber: string;
  supplier: string;
  orderDate: string;
  deliveryDate: string;
  totalAmount: string;
  itemCount: number;
  status: 'Draft' | 'Submitted' | 'Approved' | 'Received' | 'Cancelled';
  buyer: string;
}

export const purchaseOrders: PurchaseOrder[] = [
  { id: 1, poNumber: 'PO-2024-001', supplier: 'Tech Components Ltd', orderDate: '2024-01-15', deliveryDate: '2024-02-01', totalAmount: '$45,600', itemCount: 120, status: 'Received', buyer: 'John Adams' },
  { id: 2, poNumber: 'PO-2024-002', supplier: 'Office Supplies Co', orderDate: '2024-01-20', deliveryDate: '2024-02-05', totalAmount: '$3,250', itemCount: 45, status: 'Received', buyer: 'Mary Johnson' },
  { id: 3, poNumber: 'PO-2024-003', supplier: 'Industrial Materials Inc', orderDate: '2024-02-01', deliveryDate: '2024-02-20', totalAmount: '$128,900', itemCount: 85, status: 'Approved', buyer: 'John Adams' },
  { id: 4, poNumber: 'PO-2024-004', supplier: 'Electronics Wholesale', orderDate: '2024-02-05', deliveryDate: '2024-02-25', totalAmount: '$67,800', itemCount: 200, status: 'Submitted', buyer: 'Sarah Williams' },
  { id: 5, poNumber: 'PO-2024-005', supplier: 'Raw Materials Corp', orderDate: '2024-02-10', deliveryDate: '2024-03-01', totalAmount: '$234,500', itemCount: 50, status: 'Approved', buyer: 'Mary Johnson' },
  { id: 6, poNumber: 'PO-2024-006', supplier: 'Packaging Solutions', orderDate: '2024-02-12', deliveryDate: '2024-02-28', totalAmount: '$18,900', itemCount: 500, status: 'Draft', buyer: 'John Adams' },
  { id: 7, poNumber: 'PO-2024-007', supplier: 'Tech Components Ltd', orderDate: '2024-02-15', deliveryDate: '2024-03-05', totalAmount: '$89,200', itemCount: 180, status: 'Submitted', buyer: 'Sarah Williams' },
  { id: 8, poNumber: 'PO-2024-008', supplier: 'Safety Equipment Inc', orderDate: '2024-02-18', deliveryDate: '2024-03-10', totalAmount: '$12,400', itemCount: 75, status: 'Cancelled', buyer: 'Mary Johnson' },
  { id: 9, poNumber: 'PO-2024-009', supplier: 'Furniture Depot', orderDate: '2024-02-20', deliveryDate: '2024-03-15', totalAmount: '$56,700', itemCount: 25, status: 'Draft', buyer: 'John Adams' },
  { id: 10, poNumber: 'PO-2024-010', supplier: 'Chemical Supplies Ltd', orderDate: '2024-02-22', deliveryDate: '2024-03-20', totalAmount: '$142,300', itemCount: 40, status: 'Approved', buyer: 'Sarah Williams' },
];

export const purchaseOrderColumns = [
  { key: 'poNumber' as const, label: 'PO Number', editable: false },
  { key: 'supplier' as const, label: 'Supplier', editable: true },
  { key: 'orderDate' as const, label: 'Order Date', editable: true },
  { key: 'totalAmount' as const, label: 'Total Amount', editable: true },
  { key: 'itemCount' as const, label: 'Items', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
