export interface Supplier {
  id: number;
  name: string;
  category: string;
  contactName: string;
  email: string;
  phone: string;
  rating: number;
  leadTime: string;
  status: 'Active' | 'Inactive' | 'Pending Approval';
}

export const suppliers: Supplier[] = [
  { id: 1, name: 'Tech Components Ltd', category: 'Electronics', contactName: 'Alan Parker', email: 'aparker@techcomp.com', phone: '555-2001', rating: 4.8, leadTime: '5-7 days', status: 'Active' },
  { id: 2, name: 'Industrial Materials Inc', category: 'Raw Materials', contactName: 'Susan Wright', email: 'swright@indmat.com', phone: '555-2002', rating: 4.5, leadTime: '10-14 days', status: 'Active' },
  { id: 3, name: 'Office Supplies Co', category: 'Office Supplies', contactName: 'Mark Thompson', email: 'mthompson@officesup.com', phone: '555-2003', rating: 4.2, leadTime: '2-3 days', status: 'Active' },
  { id: 4, name: 'Electronics Wholesale', category: 'Electronics', contactName: 'Linda Chen', email: 'lchen@elecwhole.com', phone: '555-2004', rating: 4.6, leadTime: '7-10 days', status: 'Active' },
  { id: 5, name: 'Raw Materials Corp', category: 'Raw Materials', contactName: 'John Mitchell', email: 'jmitchell@rawmat.com', phone: '555-2005', rating: 3.9, leadTime: '14-21 days', status: 'Active' },
  { id: 6, name: 'Packaging Solutions', category: 'Packaging', contactName: 'Emily Davis', email: 'edavis@packsol.com', phone: '555-2006', rating: 4.4, leadTime: '3-5 days', status: 'Active' },
  { id: 7, name: 'Safety Equipment Inc', category: 'Safety', contactName: 'Robert Kim', email: 'rkim@safetyeq.com', phone: '555-2007', rating: 4.7, leadTime: '5-7 days', status: 'Active' },
  { id: 8, name: 'Furniture Depot', category: 'Furniture', contactName: 'Nancy Brown', email: 'nbrown@furndepot.com', phone: '555-2008', rating: 3.8, leadTime: '14-21 days', status: 'Inactive' },
  { id: 9, name: 'Chemical Supplies Ltd', category: 'Chemicals', contactName: 'David Lee', email: 'dlee@chemsup.com', phone: '555-2009', rating: 4.3, leadTime: '7-10 days', status: 'Active' },
  { id: 10, name: 'Global Parts Network', category: 'Hardware', contactName: 'Jessica Wang', email: 'jwang@globalparts.com', phone: '555-2010', rating: 4.1, leadTime: '10-14 days', status: 'Pending Approval' },
];

export const supplierColumns = [
  { key: 'name' as const, label: 'Supplier Name', editable: true },
  { key: 'category' as const, label: 'Category', editable: true },
  { key: 'contactName' as const, label: 'Contact', editable: true },
  { key: 'email' as const, label: 'Email', editable: true },
  { key: 'rating' as const, label: 'Rating', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
