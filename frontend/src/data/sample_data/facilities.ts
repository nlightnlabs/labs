export interface Facility {
  id: number;
  name: string;
  type: 'Warehouse' | 'Office' | 'Manufacturing' | 'Distribution Center' | 'Retail Store';
  address: string;
  city: string;
  capacity: string;
  utilization: number;
  manager: string;
  status: 'Operational' | 'Under Maintenance' | 'Closed';
}

export const facilities: Facility[] = [
  { id: 1, name: 'Main Distribution Hub', type: 'Distribution Center', address: '1234 Industrial Blvd', city: 'Chicago, IL', capacity: '500,000 sq ft', utilization: 85, manager: 'Robert Chen', status: 'Operational' },
  { id: 2, name: 'West Coast Warehouse', type: 'Warehouse', address: '5678 Harbor Way', city: 'Los Angeles, CA', capacity: '250,000 sq ft', utilization: 72, manager: 'Maria Santos', status: 'Operational' },
  { id: 3, name: 'Corporate Headquarters', type: 'Office', address: '100 Business Park Dr', city: 'New York, NY', capacity: '45,000 sq ft', utilization: 90, manager: 'James Wilson', status: 'Operational' },
  { id: 4, name: 'Manufacturing Plant A', type: 'Manufacturing', address: '789 Factory Lane', city: 'Detroit, MI', capacity: '320,000 sq ft', utilization: 78, manager: 'Thomas Lee', status: 'Operational' },
  { id: 5, name: 'Southeast Distribution', type: 'Distribution Center', address: '456 Logistics Pkwy', city: 'Atlanta, GA', capacity: '380,000 sq ft', utilization: 65, manager: 'Patricia Brown', status: 'Operational' },
  { id: 6, name: 'Tech Innovation Center', type: 'Office', address: '200 Tech Campus Dr', city: 'Austin, TX', capacity: '75,000 sq ft', utilization: 82, manager: 'David Kim', status: 'Operational' },
  { id: 7, name: 'Flagship Store', type: 'Retail Store', address: '888 Main Street', city: 'San Francisco, CA', capacity: '15,000 sq ft', utilization: 95, manager: 'Jennifer Lopez', status: 'Operational' },
  { id: 8, name: 'Regional Warehouse East', type: 'Warehouse', address: '321 Storage Rd', city: 'Philadelphia, PA', capacity: '180,000 sq ft', utilization: 45, manager: 'Michael Adams', status: 'Under Maintenance' },
  { id: 9, name: 'Manufacturing Plant B', type: 'Manufacturing', address: '567 Assembly Ave', city: 'Phoenix, AZ', capacity: '280,000 sq ft', utilization: 0, manager: 'None', status: 'Closed' },
  { id: 10, name: 'Downtown Retail', type: 'Retail Store', address: '50 Shopping Plaza', city: 'Seattle, WA', capacity: '12,000 sq ft', utilization: 88, manager: 'Amanda White', status: 'Operational' },
];

export const facilityColumns = [
  { key: 'name' as const, label: 'Facility Name', editable: true },
  { key: 'type' as const, label: 'Type', editable: true },
  { key: 'city' as const, label: 'Location', editable: true },
  { key: 'capacity' as const, label: 'Capacity', editable: true },
  { key: 'utilization' as const, label: 'Utilization %', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
