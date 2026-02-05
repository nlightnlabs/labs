export interface Opportunity {
  id: number;
  name: string;
  account: string;
  stage: 'Prospecting' | 'Qualification' | 'Proposal' | 'Negotiation' | 'Closed Won' | 'Closed Lost';
  amount: string;
  probability: number;
  closeDate: string;
  owner: string;
  status: 'Open' | 'Closed';
}

export const opportunities: Opportunity[] = [
  { id: 1, name: 'Enterprise License Deal', account: 'Acme Corporation', stage: 'Negotiation', amount: '$450,000', probability: 75, closeDate: '2024-03-15', owner: 'John Smith', status: 'Open' },
  { id: 2, name: 'Cloud Migration Project', account: 'Global Industries', stage: 'Proposal', amount: '$280,000', probability: 50, closeDate: '2024-04-01', owner: 'Sarah Johnson', status: 'Open' },
  { id: 3, name: 'Security Audit Services', account: 'Financial Plus Corp', stage: 'Qualification', amount: '$95,000', probability: 30, closeDate: '2024-05-20', owner: 'Mike Davis', status: 'Open' },
  { id: 4, name: 'Data Analytics Platform', account: 'Retail Giants LLC', stage: 'Closed Won', amount: '$620,000', probability: 100, closeDate: '2024-01-10', owner: 'Emily Chen', status: 'Closed' },
  { id: 5, name: 'Mobile App Development', account: 'TechStart Inc', stage: 'Prospecting', amount: '$150,000', probability: 20, closeDate: '2024-06-30', owner: 'John Smith', status: 'Open' },
  { id: 6, name: 'IT Infrastructure Upgrade', account: 'HealthFirst Medical', stage: 'Proposal', amount: '$380,000', probability: 60, closeDate: '2024-03-28', owner: 'Sarah Johnson', status: 'Open' },
  { id: 7, name: 'Consulting Services', account: 'EcoGreen Solutions', stage: 'Closed Lost', amount: '$75,000', probability: 0, closeDate: '2024-01-25', owner: 'Mike Davis', status: 'Closed' },
  { id: 8, name: 'Hardware Refresh', account: 'MediaMax Studios', stage: 'Negotiation', amount: '$210,000', probability: 80, closeDate: '2024-02-28', owner: 'Emily Chen', status: 'Open' },
  { id: 9, name: 'Training Program', account: 'BuildRight Construction', stage: 'Qualification', amount: '$45,000', probability: 40, closeDate: '2024-04-15', owner: 'John Smith', status: 'Open' },
  { id: 10, name: 'Support Contract Renewal', account: 'Logistics Pro', stage: 'Closed Won', amount: '$180,000', probability: 100, closeDate: '2024-02-01', owner: 'Sarah Johnson', status: 'Closed' },
];

export const opportunityColumns = [
  { key: 'name' as const, label: 'Opportunity Name', editable: true },
  { key: 'account' as const, label: 'Account', editable: true },
  { key: 'stage' as const, label: 'Stage', editable: true },
  { key: 'amount' as const, label: 'Amount', editable: true },
  { key: 'probability' as const, label: 'Probability %', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
