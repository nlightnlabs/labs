export interface Invoice {
  id: number;
  invoiceNumber: string;
  customer: string;
  issueDate: string;
  dueDate: string;
  amount: string;
  paidAmount: string;
  status: 'Draft' | 'Sent' | 'Paid' | 'Overdue' | 'Cancelled';
  paymentTerms: string;
}

export const invoices: Invoice[] = [
  { id: 1, invoiceNumber: 'INV-2024-001', customer: 'Acme Corporation', issueDate: '2024-01-05', dueDate: '2024-02-05', amount: '$125,000', paidAmount: '$125,000', status: 'Paid', paymentTerms: 'Net 30' },
  { id: 2, invoiceNumber: 'INV-2024-002', customer: 'Global Industries', issueDate: '2024-01-10', dueDate: '2024-02-10', amount: '$89,500', paidAmount: '$89,500', status: 'Paid', paymentTerms: 'Net 30' },
  { id: 3, invoiceNumber: 'INV-2024-003', customer: 'Retail Giants LLC', issueDate: '2024-01-15', dueDate: '2024-02-15', amount: '$234,800', paidAmount: '$0', status: 'Overdue', paymentTerms: 'Net 30' },
  { id: 4, invoiceNumber: 'INV-2024-004', customer: 'Financial Plus Corp', issueDate: '2024-01-20', dueDate: '2024-03-20', amount: '$67,200', paidAmount: '$67,200', status: 'Paid', paymentTerms: 'Net 60' },
  { id: 5, invoiceNumber: 'INV-2024-005', customer: 'HealthFirst Medical', issueDate: '2024-02-01', dueDate: '2024-03-01', amount: '$156,400', paidAmount: '$0', status: 'Sent', paymentTerms: 'Net 30' },
  { id: 6, invoiceNumber: 'INV-2024-006', customer: 'MediaMax Studios', issueDate: '2024-02-05', dueDate: '2024-03-05', amount: '$42,800', paidAmount: '$21,400', status: 'Sent', paymentTerms: 'Net 30' },
  { id: 7, invoiceNumber: 'INV-2024-007', customer: 'Logistics Pro', issueDate: '2024-02-10', dueDate: '2024-03-10', amount: '$98,600', paidAmount: '$0', status: 'Sent', paymentTerms: 'Net 30' },
  { id: 8, invoiceNumber: 'INV-2024-008', customer: 'TechStart Inc', issueDate: '2024-02-15', dueDate: '2024-03-15', amount: '$28,900', paidAmount: '$0', status: 'Draft', paymentTerms: 'Net 30' },
  { id: 9, invoiceNumber: 'INV-2024-009', customer: 'EcoGreen Solutions', issueDate: '2024-02-18', dueDate: '2024-04-18', amount: '$75,300', paidAmount: '$0', status: 'Cancelled', paymentTerms: 'Net 60' },
  { id: 10, invoiceNumber: 'INV-2024-010', customer: 'BuildRight Construction', issueDate: '2024-02-20', dueDate: '2024-03-20', amount: '$189,400', paidAmount: '$0', status: 'Sent', paymentTerms: 'Net 30' },
];

export const invoiceColumns = [
  { key: 'invoiceNumber' as const, label: 'Invoice #', editable: false },
  { key: 'customer' as const, label: 'Customer', editable: true },
  { key: 'issueDate' as const, label: 'Issue Date', editable: true },
  { key: 'dueDate' as const, label: 'Due Date', editable: true },
  { key: 'amount' as const, label: 'Amount', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
