export interface Account {
  id: number;
  name: string;
  industry: string;
  type: 'Customer' | 'Partner' | 'Prospect';
  revenue: string;
  employees: number;
  status: 'Active' | 'Inactive';
  website: string;
  phone: string;
}

export const accounts: Account[] = [
  { id: 1, name: 'Acme Corporation', industry: 'Technology', type: 'Customer', revenue: '$5,200,000', employees: 250, status: 'Active', website: 'www.acme.com', phone: '555-0101' },
  { id: 2, name: 'Global Industries', industry: 'Manufacturing', type: 'Customer', revenue: '$12,800,000', employees: 1200, status: 'Active', website: 'www.globalind.com', phone: '555-0102' },
  { id: 3, name: 'TechStart Inc', industry: 'Technology', type: 'Prospect', revenue: '$800,000', employees: 45, status: 'Active', website: 'www.techstart.io', phone: '555-0103' },
  { id: 4, name: 'Retail Giants LLC', industry: 'Retail', type: 'Customer', revenue: '$45,000,000', employees: 5000, status: 'Active', website: 'www.retailgiants.com', phone: '555-0104' },
  { id: 5, name: 'HealthFirst Medical', industry: 'Healthcare', type: 'Partner', revenue: '$8,500,000', employees: 320, status: 'Active', website: 'www.healthfirst.com', phone: '555-0105' },
  { id: 6, name: 'EcoGreen Solutions', industry: 'Environmental', type: 'Prospect', revenue: '$1,200,000', employees: 60, status: 'Active', website: 'www.ecogreen.com', phone: '555-0106' },
  { id: 7, name: 'Financial Plus Corp', industry: 'Finance', type: 'Customer', revenue: '$22,000,000', employees: 800, status: 'Active', website: 'www.finplus.com', phone: '555-0107' },
  { id: 8, name: 'BuildRight Construction', industry: 'Construction', type: 'Customer', revenue: '$15,600,000', employees: 450, status: 'Inactive', website: 'www.buildright.com', phone: '555-0108' },
  { id: 9, name: 'MediaMax Studios', industry: 'Entertainment', type: 'Partner', revenue: '$6,300,000', employees: 180, status: 'Active', website: 'www.mediamax.com', phone: '555-0109' },
  { id: 10, name: 'Logistics Pro', industry: 'Transportation', type: 'Customer', revenue: '$9,800,000', employees: 520, status: 'Active', website: 'www.logisticspro.com', phone: '555-0110' },
];

export const accountColumns = [
  { key: 'name' as const, label: 'Account Name', editable: true },
  { key: 'industry' as const, label: 'Industry', editable: true },
  { key: 'type' as const, label: 'Type', editable: true },
  { key: 'revenue' as const, label: 'Annual Revenue', editable: true },
  { key: 'employees' as const, label: 'Employees', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
