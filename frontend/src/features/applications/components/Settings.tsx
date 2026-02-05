import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Avatar,
  Toggle,
  Select,
  Modal,
  Input,
} from '@/components/common';

interface SettingsProps {
  appName: string;
}

// Mock data for users
const mockUsers = [
  { id: '1', name: 'John Doe', email: 'john@example.com', role: 'admin', status: 'active', lastActive: '2 hours ago' },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'manager', status: 'active', lastActive: '1 day ago' },
  { id: '3', name: 'Bob Johnson', email: 'bob@example.com', role: 'user', status: 'inactive', lastActive: '1 week ago' },
  { id: '4', name: 'Alice Brown', email: 'alice@example.com', role: 'user', status: 'active', lastActive: '5 minutes ago' },
];

// Mock data for roles
const mockRoles = [
  { id: '1', name: 'Admin', description: 'Full system access', userCount: 2, color: 'error' as const },
  { id: '2', name: 'Manager', description: 'Can manage users and content', userCount: 5, color: 'warning' as const },
  { id: '3', name: 'User', description: 'Standard user access', userCount: 25, color: 'info' as const },
  { id: '4', name: 'Viewer', description: 'Read-only access', userCount: 10, color: 'secondary' as const },
];

// Mock permissions
const mockPermissions = [
  { id: '1', category: 'Users', name: 'View Users', description: 'Can view user list and profiles', enabled: true },
  { id: '2', category: 'Users', name: 'Create Users', description: 'Can create new user accounts', enabled: true },
  { id: '3', category: 'Users', name: 'Edit Users', description: 'Can modify user information', enabled: true },
  { id: '4', category: 'Users', name: 'Delete Users', description: 'Can remove user accounts', enabled: false },
  { id: '5', category: 'Content', name: 'View Content', description: 'Can view all content', enabled: true },
  { id: '6', category: 'Content', name: 'Create Content', description: 'Can create new content', enabled: true },
  { id: '7', category: 'Content', name: 'Edit Content', description: 'Can modify existing content', enabled: false },
  { id: '8', category: 'Content', name: 'Delete Content', description: 'Can remove content', enabled: false },
  { id: '9', category: 'Settings', name: 'View Settings', description: 'Can view application settings', enabled: true },
  { id: '10', category: 'Settings', name: 'Modify Settings', description: 'Can change application settings', enabled: false },
];

const settingsSections = [
  { id: 'users', label: 'Users', icon: 'users' },
  { id: 'roles', label: 'Roles', icon: 'shield' },
  { id: 'permissions', label: 'Permissions', icon: 'lock' },
  { id: 'general', label: 'General', icon: 'settings' },
];

// Icons for the sidebar
const SectionIcon: React.FC<{ icon: string; className?: string }> = ({ icon, className }) => {
  const icons: Record<string, JSX.Element> = {
    users: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    shield: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    lock: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    settings: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  };
  return icons[icon] || null;
};

const Settings: React.FC<SettingsProps> = ({ appName }) => {
  const [activeSection, setActiveSection] = useState('users');
  const [users] = useState(mockUsers);
  const [roles] = useState(mockRoles);
  const [permissions, setPermissions] = useState(mockPermissions);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('user');
  const [newRoleName, setNewRoleName] = useState('');
  const [newRoleDescription, setNewRoleDescription] = useState('');

  // General settings state
  const [generalSettings, setGeneralSettings] = useState({
    appDisplayName: appName,
    allowPublicAccess: false,
    requireMfa: true,
    sessionTimeout: '30',
    maxLoginAttempts: '5',
    enableAuditLogs: true,
    enableNotifications: true,
  });

  const handlePermissionToggle = (permissionId: string) => {
    setPermissions((prev) =>
      prev.map((p) => (p.id === permissionId ? { ...p, enabled: !p.enabled } : p))
    );
  };

  const handleInviteUser = () => {
    console.log('Inviting user:', inviteEmail, 'with role:', inviteRole);
    setIsInviteModalOpen(false);
    setInviteEmail('');
    setInviteRole('user');
  };

  const handleCreateRole = () => {
    console.log('Creating role:', newRoleName, newRoleDescription);
    setIsRoleModalOpen(false);
    setNewRoleName('');
    setNewRoleDescription('');
  };

  // Group permissions by category
  const permissionsByCategory = permissions.reduce((acc, permission) => {
    if (!acc[permission.category]) {
      acc[permission.category] = [];
    }
    acc[permission.category].push(permission);
    return acc;
  }, {} as Record<string, typeof permissions>);

  const renderContent = () => {
    switch (activeSection) {
      case 'users':
        return (
          <Card>
            <CardHeader
              title="User Management"
              subtitle="Manage users who have access to this application"
              action={
                <Button size="sm" onClick={() => setIsInviteModalOpen(true)}>
                  Invite User
                </Button>
              }
            />
            <CardBody>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b" style={{ borderColor: 'var(--border-default)' }}>
                      <th className="text-left py-3 px-4 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>User</th>
                      <th className="text-left py-3 px-4 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Role</th>
                      <th className="text-left py-3 px-4 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Last Active</th>
                      <th className="text-right py-3 px-4 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b" style={{ borderColor: 'var(--border-default)' }}>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-3">
                            <Avatar name={user.name} size="sm" />
                            <div>
                              <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>{user.name}</p>
                              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{user.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge
                            variant={user.role === 'admin' ? 'error' : user.role === 'manager' ? 'warning' : 'info'}
                            size="sm"
                          >
                            {user.role}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant={user.status === 'active' ? 'success' : 'secondary'} size="sm">
                            {user.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                          {user.lastActive}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button variant="ghost" size="sm">Edit</Button>
                          <Button variant="ghost" size="sm" className="text-red-600">Remove</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>
        );

      case 'roles':
        return (
          <Card>
            <CardHeader
              title="Role Management"
              subtitle="Define roles and their access levels"
              action={
                <Button size="sm" onClick={() => setIsRoleModalOpen(true)}>
                  Create Role
                </Button>
              }
            />
            <CardBody>
              <div className="grid gap-4 md:grid-cols-2">
                {roles.map((role) => (
                  <div
                    key={role.id}
                    className="p-4 rounded-lg border"
                    style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--bg-subtle)' }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant={role.color}>{role.name}</Badge>
                      </div>
                      <Button variant="ghost" size="sm">Edit</Button>
                    </div>
                    <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {role.description}
                    </p>
                    <p className="mt-2 text-xs" style={{ color: 'var(--text-tertiary)' }}>
                      {role.userCount} users assigned
                    </p>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        );

      case 'permissions':
        return (
          <div className="space-y-4">
            {Object.entries(permissionsByCategory).map(([category, categoryPermissions]) => (
              <Card key={category}>
                <CardHeader title={category} subtitle={`Manage ${category.toLowerCase()} permissions`} />
                <CardBody>
                  <div className="space-y-4">
                    {categoryPermissions.map((permission) => (
                      <div
                        key={permission.id}
                        className="flex items-center justify-between py-2 border-b last:border-b-0"
                        style={{ borderColor: 'var(--border-default)' }}
                      >
                        <div>
                          <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                            {permission.name}
                          </p>
                          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                            {permission.description}
                          </p>
                        </div>
                        <Toggle
                          checked={permission.enabled}
                          onChange={() => handlePermissionToggle(permission.id)}
                        />
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        );

      case 'general':
        return (
          <div className="space-y-4">
            <Card>
              <CardHeader title="Application Settings" subtitle="Configure general application behavior" />
              <CardBody>
                <div className="space-y-4 max-w-lg">
                  <Input
                    label="Application Display Name"
                    value={generalSettings.appDisplayName}
                    onChange={(e) => setGeneralSettings({ ...generalSettings, appDisplayName: e.target.value })}
                  />
                  <Select
                    label="Session Timeout (minutes)"
                    value={generalSettings.sessionTimeout}
                    onChange={(value) => setGeneralSettings({ ...generalSettings, sessionTimeout: value })}
                    options={[
                      { value: '15', label: '15 minutes' },
                      { value: '30', label: '30 minutes' },
                      { value: '60', label: '1 hour' },
                      { value: '120', label: '2 hours' },
                    ]}
                  />
                  <Select
                    label="Max Login Attempts"
                    value={generalSettings.maxLoginAttempts}
                    onChange={(value) => setGeneralSettings({ ...generalSettings, maxLoginAttempts: value })}
                    options={[
                      { value: '3', label: '3 attempts' },
                      { value: '5', label: '5 attempts' },
                      { value: '10', label: '10 attempts' },
                    ]}
                  />
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Security Settings" subtitle="Configure security options for the application" />
              <CardBody>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                        Allow Public Access
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Allow unauthenticated users to access public areas
                      </p>
                    </div>
                    <Toggle
                      checked={generalSettings.allowPublicAccess}
                      onChange={(checked) => setGeneralSettings({ ...generalSettings, allowPublicAccess: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                        Require Multi-Factor Authentication
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Require MFA for all users on login
                      </p>
                    </div>
                    <Toggle
                      checked={generalSettings.requireMfa}
                      onChange={(checked) => setGeneralSettings({ ...generalSettings, requireMfa: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                        Enable Audit Logs
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Track all user actions and system events
                      </p>
                    </div>
                    <Toggle
                      checked={generalSettings.enableAuditLogs}
                      onChange={(checked) => setGeneralSettings({ ...generalSettings, enableAuditLogs: checked })}
                    />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Notifications" subtitle="Configure notification preferences" />
              <CardBody>
                <div className="flex items-center justify-between py-2">
                  <div>
                    <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                      Enable Email Notifications
                    </p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      Send email notifications for important events
                    </p>
                  </div>
                  <Toggle
                    checked={generalSettings.enableNotifications}
                    onChange={(checked) => setGeneralSettings({ ...generalSettings, enableNotifications: checked })}
                  />
                </div>
              </CardBody>
            </Card>

            <div className="flex justify-end gap-3">
              <Button variant="outline">Cancel</Button>
              <Button>Save Changes</Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex gap-6">
      {/* Left Sidebar Navigation */}
      <div className="w-48 flex-shrink-0">
        <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
          Manage users, roles, permissions, and application settings
        </p>
        <nav className="space-y-1">
          {settingsSections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeSection === section.id
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
              style={{
                color: activeSection === section.id ? undefined : 'var(--text-secondary)',
              }}
            >
              <SectionIcon icon={section.icon} className="w-5 h-5" />
              {section.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 min-w-0">
        {renderContent()}
      </div>

      {/* Invite User Modal */}
      <Modal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        title="Invite User"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setIsInviteModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleInviteUser}>Send Invite</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            placeholder="user@example.com"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
          />
          <Select
            label="Role"
            value={inviteRole}
            onChange={(value) => setInviteRole(value)}
            options={[
              { value: 'admin', label: 'Admin' },
              { value: 'manager', label: 'Manager' },
              { value: 'user', label: 'User' },
              { value: 'viewer', label: 'Viewer' },
            ]}
          />
        </div>
      </Modal>

      {/* Create Role Modal */}
      <Modal
        isOpen={isRoleModalOpen}
        onClose={() => setIsRoleModalOpen(false)}
        title="Create Role"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setIsRoleModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateRole}>Create Role</Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            label="Role Name"
            placeholder="e.g., Editor"
            value={newRoleName}
            onChange={(e) => setNewRoleName(e.target.value)}
          />
          <Input
            label="Description"
            placeholder="Describe the role's purpose"
            value={newRoleDescription}
            onChange={(e) => setNewRoleDescription(e.target.value)}
          />
        </div>
      </Modal>
    </div>
  );
};

export default Settings;
