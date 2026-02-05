export interface Employee {
  id: number;
  employeeId: string;
  firstName: string;
  lastName: string;
  email: string;
  department: string;
  title: string;
  hireDate: string;
  salary: string;
  status: 'Active' | 'On Leave' | 'Terminated';
}

export const employees: Employee[] = [
  { id: 1, employeeId: 'EMP-001', firstName: 'John', lastName: 'Smith', email: 'jsmith@company.com', department: 'Engineering', title: 'Senior Developer', hireDate: '2020-03-15', salary: '$125,000', status: 'Active' },
  { id: 2, employeeId: 'EMP-002', firstName: 'Sarah', lastName: 'Johnson', email: 'sjohnson@company.com', department: 'Sales', title: 'Sales Manager', hireDate: '2019-07-01', salary: '$95,000', status: 'Active' },
  { id: 3, employeeId: 'EMP-003', firstName: 'Michael', lastName: 'Davis', email: 'mdavis@company.com', department: 'Marketing', title: 'Marketing Director', hireDate: '2018-11-20', salary: '$135,000', status: 'Active' },
  { id: 4, employeeId: 'EMP-004', firstName: 'Emily', lastName: 'Chen', email: 'echen@company.com', department: 'Engineering', title: 'Software Engineer', hireDate: '2021-06-10', salary: '$98,000', status: 'Active' },
  { id: 5, employeeId: 'EMP-005', firstName: 'Robert', lastName: 'Wilson', email: 'rwilson@company.com', department: 'Finance', title: 'Financial Analyst', hireDate: '2020-09-05', salary: '$85,000', status: 'Active' },
  { id: 6, employeeId: 'EMP-006', firstName: 'Lisa', lastName: 'Anderson', email: 'landerson@company.com', department: 'HR', title: 'HR Manager', hireDate: '2019-02-14', salary: '$92,000', status: 'On Leave' },
  { id: 7, employeeId: 'EMP-007', firstName: 'David', lastName: 'Martinez', email: 'dmartinez@company.com', department: 'Operations', title: 'Operations Lead', hireDate: '2017-08-22', salary: '$88,000', status: 'Active' },
  { id: 8, employeeId: 'EMP-008', firstName: 'Jennifer', lastName: 'Taylor', email: 'jtaylor@company.com', department: 'Engineering', title: 'Tech Lead', hireDate: '2018-04-30', salary: '$145,000', status: 'Active' },
  { id: 9, employeeId: 'EMP-009', firstName: 'James', lastName: 'Brown', email: 'jbrown@company.com', department: 'Sales', title: 'Account Executive', hireDate: '2022-01-10', salary: '$75,000', status: 'Terminated' },
  { id: 10, employeeId: 'EMP-010', firstName: 'Amanda', lastName: 'White', email: 'awhite@company.com', department: 'Customer Support', title: 'Support Manager', hireDate: '2020-11-18', salary: '$78,000', status: 'Active' },
];

export const employeeColumns = [
  { key: 'employeeId' as const, label: 'Employee ID', editable: false },
  { key: 'firstName' as const, label: 'First Name', editable: true },
  { key: 'lastName' as const, label: 'Last Name', editable: true },
  { key: 'department' as const, label: 'Department', editable: true },
  { key: 'title' as const, label: 'Title', editable: true },
  { key: 'status' as const, label: 'Status', editable: true },
];
