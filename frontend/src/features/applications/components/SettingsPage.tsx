import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  Tabs,
  TabPanel,
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

const tabs = [
  { id: 'users', label: 'Users' },
  { id: 'roles', label: 'Roles' },
  { id: 'permissions', label: 'Permissions' },
  { id: 'general', label: 'General' },
];

export const SettingsPage: React.FC<SettingsProps> = ({ appName }) => {

  const { t } = useTranslation();

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('modules.settings.title')}
        </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
            Manage users, roles, permissions, and application settings
          </p>
        </div>
      </div>

      <Tabs tabs={tabs} defaultTab="users">
        {/* Users Tab */}
        <TabPanel tabId="users">
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
        </TabPanel>

        {/* Roles Tab */}
        <TabPanel tabId="roles">
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
        </TabPanel>

        {/* Permissions Tab */}
        <TabPanel tabId="permissions">
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
        </TabPanel>

        {/* General Tab */}
        <TabPanel tabId="general">
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
        </TabPanel>
      </Tabs>

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

export default SettingsPage;
