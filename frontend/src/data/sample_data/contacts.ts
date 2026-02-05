export interface Contact {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  account: string;
  title: string;
  department: string;
  status: 'Active' | 'Inactive';
}

export const contacts: Contact[] = [
  { id: 1, firstName: 'James', lastName: 'Wilson', email: 'jwilson@acme.com', phone: '555-1001', account: 'Acme Corporation', title: 'VP of Engineering', department: 'Engineering', status: 'Active' },
  { id: 2, firstName: 'Lisa', lastName: 'Anderson', email: 'landerson@globalind.com', phone: '555-1002', account: 'Global Industries', title: 'CTO', department: 'Technology', status: 'Active' },
  { id: 3, firstName: 'Robert', lastName: 'Martinez', email: 'rmartinez@techstart.io', phone: '555-1003', account: 'TechStart Inc', title: 'CEO', department: 'Executive', status: 'Active' },
  { id: 4, firstName: 'Jennifer', lastName: 'Taylor', email: 'jtaylor@retailgiants.com', phone: '555-1004', account: 'Retail Giants LLC', title: 'Procurement Manager', department: 'Procurement', status: 'Active' },
  { id: 5, firstName: 'Michael', lastName: 'Brown', email: 'mbrown@healthfirst.com', phone: '555-1005', account: 'HealthFirst Medical', title: 'IT Director', department: 'IT', status: 'Active' },
  { id: 6, firstName: 'Amanda', lastName: 'Davis', email: 'adavis@ecogreen.com', phone: '555-1006', account: 'EcoGreen Solutions', title: 'Operations Manager', department: 'Operations', status: 'Active' },
  { id: 7, firstName: 'David', lastName: 'Miller', email: 'dmiller@finplus.com', phone: '555-1007', account: 'Financial Plus Corp', title: 'CFO', department: 'Finance', status: 'Active' },
  { id: 8, firstName: 'Sarah', lastName: 'Garcia', email: 'sgarcia@buildright.com', phone: '555-1008', account: 'BuildRight Construction', title: 'Project Director', department: 'Projects', status: 'Inactive' },
  { id: 9, firstName: 'Thomas', lastName: 'Lee', email: 'tlee@mediamax.com', phone: '555-1009', account: 'MediaMax Studios', title: 'Creative Director', department: 'Creative', status: 'Active' },
  { id: 10, firstName: 'Rachel', lastName: 'White', email: 'rwhite@logisticspro.com', phone: '555-1010', account: 'Logistics Pro', title: 'Supply Chain Manager', department: 'Supply Chain', status: 'Active' },
];

export const contactColumns = [
  { key: 'firstName' as const, label: 'First Name', editable: true },
  { key: 'lastName' as const, label: 'Last Name', editable: true },
  { key: 'email' as const, label: 'Email', editable: true },
  { key: 'account' as const, label: 'Account', editable: true },
  { key: 'title' as const, label: 'Title', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
