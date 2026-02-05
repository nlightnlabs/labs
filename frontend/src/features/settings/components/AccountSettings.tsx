import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Input, Button, Alert, Badge, Modal } from '@/components/common';
import { authApi, usersApi } from '@/services/api';
import { Session } from '@/types';

export const AccountSettings: React.FC = () => {
  const { t } = useTranslation();

  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({});
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Sessions state
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
    if (passwordErrors[name]) {
      setPasswordErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMessage(null);
    const errors: Record<string, string> = {};

    if (!passwordData.currentPassword) {
      errors.currentPassword = t('validation.required');
    }
    if (!passwordData.newPassword) {
      errors.newPassword = t('validation.required');
    } else if (passwordData.newPassword.length < 8) {
      errors.newPassword = t('auth.errors.passwordMinLength');
    }
    if (passwordData.newPassword !== passwordData.confirmNewPassword) {
      errors.confirmNewPassword = t('auth.errors.passwordMismatch');
    }

    if (Object.keys(errors).length > 0) {
      setPasswordErrors(errors);
      return;
    }

    setPasswordLoading(true);
    try {
      await authApi.changePassword({
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
      });
      setPasswordMessage({ type: 'success', text: t('auth.passwordChanged') });
      setPasswordData({ currentPassword: '', newPassword: '', confirmNewPassword: '' });
    } catch (error) {
      setPasswordMessage({ type: 'error', text: t('errors.general') });
    } finally {
      setPasswordLoading(false);
    }
  };

  const loadSessions = async () => {
    setSessionsLoading(true);
    try {
      const response = await usersApi.getSessions();
      setSessions(response.data.data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setSessionsLoading(false);
    }
  };

  const revokeSession = async (sessionId: string) => {
    try {
      await usersApi.revokeSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (error) {
      console.error('Failed to revoke session:', error);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE') return;

    try {
      await authApi.deleteAccount();
      window.location.href = '/login';
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card>
        <CardHeader
          title={t('settings.account.changePassword')}
          subtitle={t('settings.account.subtitle')}
        />
        <CardBody>
          {passwordMessage && (
            <Alert
              variant={passwordMessage.type}
              className="mb-4"
              onClose={() => setPasswordMessage(null)}
            >
              {passwordMessage.text}
            </Alert>
          )}

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <Input
              label={t('settings.account.currentPassword')}
              name="currentPassword"
              type="password"
              value={passwordData.currentPassword}
              onChange={handlePasswordChange}
              error={passwordErrors.currentPassword}
            />
            <Input
              label={t('settings.account.newPassword')}
              name="newPassword"
              type="password"
              value={passwordData.newPassword}
              onChange={handlePasswordChange}
              error={passwordErrors.newPassword}
            />
            <Input
              label={t('settings.account.confirmNewPassword')}
              name="confirmNewPassword"
              type="password"
              value={passwordData.confirmNewPassword}
              onChange={handlePasswordChange}
              error={passwordErrors.confirmNewPassword}
            />
            <div className="flex justify-end">
              <Button type="submit" isLoading={passwordLoading}>
                {t('settings.account.changePassword')}
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader title={t('settings.account.twoFactor')} />
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p style={{ color: 'var(--text-primary)' }}>
                {t('settings.account.twoFactorDisabled')}
              </p>
              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                Add an extra layer of security to your account
              </p>
            </div>
            <Button variant="outline">
              {t('settings.account.enable2FA')}
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader
          title={t('settings.account.sessions')}
          action={
            <Button variant="outline" size="sm" onClick={loadSessions}>
              Refresh
            </Button>
          }
        />
        <CardBody>
          {sessionsLoading ? (
            <div className="text-center py-4">Loading...</div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-4" style={{ color: 'var(--text-secondary)' }}>
              Click refresh to load active sessions
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{ backgroundColor: 'var(--bg-hover)' }}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        {session.userAgent || 'Unknown Device'}
                      </p>
                      {session.isCurrent && (
                        <Badge variant="success" size="sm">
                          {t('settings.account.currentSession')}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {session.ipAddress} • Last active: {new Date(session.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  {!session.isCurrent && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => revokeSession(session.id)}
                    >
                      {t('settings.account.revokeSession')}
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Delete Account */}
      <Card variant="outlined" className="border-error-300">
        <CardHeader title={t('settings.account.deleteAccount')} />
        <CardBody>
          <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>
            {t('settings.account.deleteAccountWarning')}
          </p>
          <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
            {t('settings.account.deleteAccount')}
          </Button>
        </CardBody>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title={t('settings.account.deleteAccount')}
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowDeleteModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="danger"
              disabled={deleteConfirmation !== 'DELETE'}
              onClick={handleDeleteAccount}
            >
              {t('settings.account.deleteAccount')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p style={{ color: 'var(--text-secondary)' }}>
            {t('settings.account.deleteAccountWarning')}
          </p>
          <Input
            label={t('settings.account.confirmDelete')}
            value={deleteConfirmation}
            onChange={(e) => setDeleteConfirmation(e.target.value)}
            placeholder="DELETE"
          />
        </div>
      </Modal>
    </div>
  );
};

export default AccountSettings;
