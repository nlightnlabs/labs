export interface Contract {
  id: number;
  contractNumber: string;
  title: string;
  party: string;
  type: 'Service Agreement' | 'Purchase Agreement' | 'NDA' | 'Employment' | 'Lease';
  startDate: string;
  endDate: string;
  value: string;
  status: 'Active' | 'Expired' | 'Pending' | 'Terminated';
}

export const contracts: Contract[] = [
  { id: 1, contractNumber: 'CTR-2024-001', title: 'Annual IT Support', party: 'Acme Corporation', type: 'Service Agreement', startDate: '2024-01-01', endDate: '2024-12-31', value: '$480,000', status: 'Active' },
  { id: 2, contractNumber: 'CTR-2024-002', title: 'Raw Materials Supply', party: 'Industrial Materials Inc', type: 'Purchase Agreement', startDate: '2024-01-15', endDate: '2025-01-14', value: '$1,250,000', status: 'Active' },
  { id: 3, contractNumber: 'CTR-2023-015', title: 'Confidentiality Agreement', party: 'TechStart Inc', type: 'NDA', startDate: '2023-06-01', endDate: '2026-05-31', value: '$0', status: 'Active' },
  { id: 4, contractNumber: 'CTR-2024-003', title: 'Office Lease - HQ', party: 'Commercial Realty Group', type: 'Lease', startDate: '2024-02-01', endDate: '2029-01-31', value: '$2,400,000', status: 'Active' },
  { id: 5, contractNumber: 'CTR-2023-012', title: 'Consulting Services', party: 'Global Industries', type: 'Service Agreement', startDate: '2023-09-01', endDate: '2024-02-28', value: '$150,000', status: 'Expired' },
  { id: 6, contractNumber: 'CTR-2024-004', title: 'Electronics Supply', party: 'Tech Components Ltd', type: 'Purchase Agreement', startDate: '2024-03-01', endDate: '2025-02-28', value: '$890,000', status: 'Pending' },
  { id: 7, contractNumber: 'CTR-2023-008', title: 'Warehouse Lease', party: 'Industrial Properties LLC', type: 'Lease', startDate: '2023-04-01', endDate: '2028-03-31', value: '$1,800,000', status: 'Active' },
  { id: 8, contractNumber: 'CTR-2024-005', title: 'Marketing Partnership', party: 'MediaMax Studios', type: 'Service Agreement', startDate: '2024-01-01', endDate: '2024-06-30', value: '$275,000', status: 'Active' },
  { id: 9, contractNumber: 'CTR-2023-020', title: 'Logistics Services', party: 'Logistics Pro', type: 'Service Agreement', startDate: '2023-11-01', endDate: '2024-01-31', value: '$95,000', status: 'Terminated' },
  { id: 10, contractNumber: 'CTR-2024-006', title: 'Employee NDA', party: 'John Smith', type: 'Employment', startDate: '2024-02-15', endDate: '2027-02-14', value: '$0', status: 'Pending' },
];

export const contractColumns = [
  { key: 'contractNumber' as const, label: 'Contract #', editable: false },
  { key: 'title' as const, label: 'Title', editable: true },
  { key: 'party' as const, label: 'Party', editable: true },
  { key: 'type' as const, label: 'Type', editable: true },
  { key: 'value' as const, label: 'Value', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
