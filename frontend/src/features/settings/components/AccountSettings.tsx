import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Input, Button, Alert, Badge, Modal } from '@/components/common';
import { authApi, usersApi, twoFactorApi, TwoFactorMethod } from '@/services/api';
import { useAppSelector } from '@/store/hooks';
import { Session } from '@/types';

export const AccountSettings: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAppSelector((state) => state.auth);

  // Username state
  const [username, setUsername] = useState(user?.username || '');
  const [usernameLoading, setUsernameLoading] = useState(false);
  const [usernameMessage, setUsernameMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({});
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // 2FA state
  const [show2FAModal, setShow2FAModal] = useState(false);
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [twoFAMethod, setTwoFAMethod] = useState<TwoFactorMethod>('authenticator');
  const [twoFAContactInfo, setTwoFAContactInfo] = useState('');
  const [twoFAVerificationCode, setTwoFAVerificationCode] = useState('');
  const [twoFAStep, setTwoFAStep] = useState<'select' | 'verify'>('select');
  const [twoFASetupData, setTwoFASetupData] = useState<{
    qr_code_url?: string;
    secret?: string;
    backup_codes?: string[];
    message?: string;
  } | null>(null);
  const [twoFALoading, setTwoFALoading] = useState(false);
  const [twoFAMessage, setTwoFAMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Sessions state
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');

  // Fetch 2FA status on mount
  useEffect(() => {
    const fetch2FAStatus = async () => {
      if (!user?.id) return;
      try {
        const response = await twoFactorApi.getStatus(user.id);
        setTwoFAEnabled(response.data.enabled);
        if (response.data.method) {
          setTwoFAMethod(response.data.method);
        }
      } catch (error) {
        console.error('Failed to fetch 2FA status:', error);
      }
    };
    fetch2FAStatus();
  }, [user?.id]);

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
        username: user?.username || user?.email || '',
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

  const handleUsernameSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    setUsernameLoading(true);
    setUsernameMessage(null);
    try {
      await authApi.updateProfile({ username });
      setUsernameMessage({ type: 'success', text: 'Username updated successfully' });
    } catch (error) {
      setUsernameMessage({ type: 'error', text: 'Failed to update username' });
    } finally {
      setUsernameLoading(false);
    }
  };

  const handle2FASetup = async () => {
    if (!user?.id) return;

    setTwoFALoading(true);
    setTwoFAMessage(null);
    try {
      const response = await twoFactorApi.setup({
        user_id: user.id,
        method: twoFAMethod,
        contact_info: twoFAContactInfo || undefined,
      });
      setTwoFASetupData(response.data);
      if (response.data.requires_verification) {
        setTwoFAStep('verify');
      } else {
        setTwoFAEnabled(true);
        setShow2FAModal(false);
        reset2FAModal();
      }
    } catch (error) {
      setTwoFAMessage({ type: 'error', text: 'Failed to setup 2FA' });
    } finally {
      setTwoFALoading(false);
    }
  };

  const handle2FAVerify = async () => {
    if (!user?.id || !twoFAVerificationCode) return;

    setTwoFALoading(true);
    setTwoFAMessage(null);
    try {
      const response = await twoFactorApi.verify({
        user_id: user.id,
        method: twoFAMethod,
        verification_code: twoFAVerificationCode,
      });
      if (response.data.success) {
        setTwoFAEnabled(true);
        setShow2FAModal(false);
        reset2FAModal();
      } else {
        setTwoFAMessage({ type: 'error', text: 'Invalid verification code' });
      }
    } catch (error) {
      setTwoFAMessage({ type: 'error', text: 'Verification failed' });
    } finally {
      setTwoFALoading(false);
    }
  };

  const handle2FADisable = async () => {
    if (!user?.id) return;

    setTwoFALoading(true);
    try {
      await twoFactorApi.disable(user.id);
      setTwoFAEnabled(false);
      setShow2FAModal(false);
    } catch (error) {
      setTwoFAMessage({ type: 'error', text: 'Failed to disable 2FA' });
    } finally {
      setTwoFALoading(false);
    }
  };

  const reset2FAModal = () => {
    setTwoFAStep('select');
    setTwoFAMethod('authenticator');
    setTwoFAContactInfo('');
    setTwoFAVerificationCode('');
    setTwoFASetupData(null);
    setTwoFAMessage(null);
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation.toLowerCase() !== 'delete') return;

    try {
      await authApi.deleteAccount();
      window.location.href = '/login';
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Username */}
      <Card>
        <CardHeader
          title="Username"
          subtitle="Update your account username"
        />
        <CardBody>
          {usernameMessage && (
            <Alert
              variant={usernameMessage.type}
              className="mb-4"
              onClose={() => setUsernameMessage(null)}
            >
              {usernameMessage.text}
            </Alert>
          )}
          <form onSubmit={handleUsernameSubmit} className="space-y-4">
            <Input
              label="Username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />
            <div className="flex justify-end">
              <Button type="submit" isLoading={usernameLoading}>
                Update Username
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

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
                {twoFAEnabled ? 'Two-factor authentication is enabled' : t('settings.account.twoFactorDisabled')}
              </p>
              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                {twoFAEnabled
                  ? 'Your account is protected with an additional security layer'
                  : 'Add an extra layer of security to your account'}
              </p>
            </div>
            <Button
              variant={twoFAEnabled ? 'danger' : 'outline'}
              onClick={() => setShow2FAModal(true)}
            >
              {twoFAEnabled ? 'Disable 2FA' : t('settings.account.enable2FA')}
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
        onClose={() => {
          setShowDeleteModal(false);
          setDeleteConfirmation('');
        }}
        title={t('settings.account.deleteAccount')}
        footer={
          <>
            <Button variant="ghost" onClick={() => {
              setShowDeleteModal(false);
              setDeleteConfirmation('');
            }}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="danger"
              disabled={deleteConfirmation.toLowerCase() !== 'delete'}
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
          <p style={{ color: 'var(--text-primary)' }}>
            To confirm, please type <strong>delete</strong> below:
          </p>
          <Input
            label={t('settings.account.confirmDelete')}
            value={deleteConfirmation}
            onChange={(e) => setDeleteConfirmation(e.target.value)}
            placeholder="delete"
          />
        </div>
      </Modal>

      {/* 2FA Setup Modal */}
      <Modal
        isOpen={show2FAModal}
        onClose={() => {
          setShow2FAModal(false);
          reset2FAModal();
        }}
        title={twoFAEnabled ? 'Disable Two-Factor Authentication' : 'Setup Two-Factor Authentication'}
        footer={
          twoFAEnabled ? (
            <>
              <Button variant="ghost" onClick={() => setShow2FAModal(false)}>
                {t('common.cancel')}
              </Button>
              <Button
                variant="danger"
                onClick={handle2FADisable}
                isLoading={twoFALoading}
              >
                Disable 2FA
              </Button>
            </>
          ) : twoFAStep === 'select' ? (
            <>
              <Button variant="ghost" onClick={() => setShow2FAModal(false)}>
                {t('common.cancel')}
              </Button>
              <Button
                onClick={handle2FASetup}
                isLoading={twoFALoading}
                disabled={
                  (twoFAMethod === 'sms' || twoFAMethod === 'email') && !twoFAContactInfo
                }
              >
                Continue
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" onClick={() => setTwoFAStep('select')}>
                Back
              </Button>
              <Button
                onClick={handle2FAVerify}
                isLoading={twoFALoading}
                disabled={!twoFAVerificationCode}
              >
                Verify & Enable
              </Button>
            </>
          )
        }
      >
        {twoFAMessage && (
          <Alert
            variant={twoFAMessage.type}
            className="mb-4"
            onClose={() => setTwoFAMessage(null)}
          >
            {twoFAMessage.text}
          </Alert>
        )}

        {twoFAEnabled ? (
          <div className="space-y-4">
            <p style={{ color: 'var(--text-secondary)' }}>
              Are you sure you want to disable two-factor authentication? This will make your account less secure.
            </p>
          </div>
        ) : twoFAStep === 'select' ? (
          <div className="space-y-4">
            <p style={{ color: 'var(--text-secondary)' }}>
              Choose your preferred two-factor authentication method:
            </p>

            <div className="space-y-3">
              <label className="flex items-start gap-3 p-3 rounded-lg cursor-pointer border" style={{
                borderColor: twoFAMethod === 'authenticator' ? 'var(--primary)' : 'var(--border-color)',
                backgroundColor: twoFAMethod === 'authenticator' ? 'var(--bg-hover)' : 'transparent'
              }}>
                <input
                  type="radio"
                  name="2fa-method"
                  value="authenticator"
                  checked={twoFAMethod === 'authenticator'}
                  onChange={(e) => setTwoFAMethod(e.target.value as TwoFactorMethod)}
                  className="mt-1"
                />
                <div>
                  <p className="font-medium" style={{ color: 'var(--text-primary)' }}>Authenticator App</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Use an app like Google Authenticator, Authy, or 1Password
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-lg cursor-pointer border" style={{
                borderColor: twoFAMethod === 'sms' ? 'var(--primary)' : 'var(--border-color)',
                backgroundColor: twoFAMethod === 'sms' ? 'var(--bg-hover)' : 'transparent'
              }}>
                <input
                  type="radio"
                  name="2fa-method"
                  value="sms"
                  checked={twoFAMethod === 'sms'}
                  onChange={(e) => setTwoFAMethod(e.target.value as TwoFactorMethod)}
                  className="mt-1"
                />
                <div>
                  <p className="font-medium" style={{ color: 'var(--text-primary)' }}>SMS Text Message</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Receive a verification code via text message
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 rounded-lg cursor-pointer border" style={{
                borderColor: twoFAMethod === 'email' ? 'var(--primary)' : 'var(--border-color)',
                backgroundColor: twoFAMethod === 'email' ? 'var(--bg-hover)' : 'transparent'
              }}>
                <input
                  type="radio"
                  name="2fa-method"
                  value="email"
                  checked={twoFAMethod === 'email'}
                  onChange={(e) => setTwoFAMethod(e.target.value as TwoFactorMethod)}
                  className="mt-1"
                />
                <div>
                  <p className="font-medium" style={{ color: 'var(--text-primary)' }}>Email</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Receive a verification code via email
                  </p>
                </div>
              </label>
            </div>

            {twoFAMethod === 'sms' && (
              <Input
                label="Phone Number"
                type="tel"
                value={twoFAContactInfo}
                onChange={(e) => setTwoFAContactInfo(e.target.value)}
                placeholder="+1 (555) 000-0000"
              />
            )}

            {twoFAMethod === 'email' && (
              <Input
                label="Email Address"
                type="email"
                value={twoFAContactInfo}
                onChange={(e) => setTwoFAContactInfo(e.target.value)}
                placeholder="email@example.com"
              />
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {twoFAMethod === 'authenticator' && twoFASetupData?.qr_code_url && (
              <div className="text-center">
                <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>
                  Scan this QR code with your authenticator app:
                </p>
                <div className="inline-block p-4 bg-white rounded-lg">
                  <img
                    src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(twoFASetupData.qr_code_url)}`}
                    alt="2FA QR Code"
                    className="w-48 h-48"
                  />
                </div>
                {twoFASetupData.secret && (
                  <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Or enter this code manually: <code className="bg-gray-100 px-2 py-1 rounded">{twoFASetupData.secret}</code>
                  </p>
                )}
              </div>
            )}

            {(twoFAMethod === 'sms' || twoFAMethod === 'email') && (
              <p style={{ color: 'var(--text-secondary)' }}>
                {twoFASetupData?.message || `A verification code has been sent to your ${twoFAMethod === 'sms' ? 'phone' : 'email'}.`}
              </p>
            )}

            <Input
              label="Verification Code"
              value={twoFAVerificationCode}
              onChange={(e) => setTwoFAVerificationCode(e.target.value)}
              placeholder="Enter 6-digit code"
              maxLength={6}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AccountSettings;
