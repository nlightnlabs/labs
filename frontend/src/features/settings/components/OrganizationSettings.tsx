import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Input, Button, Select, Toggle, Alert, Badge, Modal } from '@/components/common';

export const OrganizationSettings: React.FC = () => {
  const { t } = useTranslation();

  const [orgData, setOrgData] = useState({
    name: 'My Organization',
    slug: 'my-organization',
  });

  const [ssoEnabled, setSsoEnabled] = useState(false);
  const [showAddProviderModal, setShowAddProviderModal] = useState(false);
  const [providers, setProviders] = useState<Array<{ id: string; name: string; type: string; isActive: boolean }>>([]);

  const [newProvider, setNewProvider] = useState({
    name: '',
    entityId: '',
    ssoUrl: '',
    certificate: '',
  });

  const roleOptions = [
    { value: 'user', label: t('settings.organization.roles.user') },
    { value: 'manager', label: t('settings.organization.roles.manager') },
    { value: 'admin', label: t('settings.organization.roles.admin') },
  ];

  const handleOrgChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setOrgData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddProvider = () => {
    const provider = {
      id: Date.now().toString(),
      name: newProvider.name,
      type: 'SAML',
      isActive: true,
    };
    setProviders((prev) => [...prev, provider]);
    setNewProvider({ name: '', entityId: '', ssoUrl: '', certificate: '' });
    setShowAddProviderModal(false);
  };

  const toggleProviderStatus = (id: string) => {
    setProviders((prev) =>
      prev.map((p) => (p.id === id ? { ...p, isActive: !p.isActive } : p))
    );
  };

  const deleteProvider = (id: string) => {
    setProviders((prev) => prev.filter((p) => p.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Organization Details */}
      <Card>
        <CardHeader
          title={t('settings.organization.title')}
          subtitle={t('settings.organization.subtitle')}
        />
        <CardBody className="space-y-4">
          <Input
            label={t('settings.organization.name')}
            name="name"
            value={orgData.name}
            onChange={handleOrgChange}
          />

          <Input
            label={t('settings.organization.slug')}
            name="slug"
            value={orgData.slug}
            onChange={handleOrgChange}
            helperText="Used in URLs: app.example.com/my-organization"
          />

          <div>
            <label className="label">{t('settings.organization.logo')}</label>
            <div className="flex items-center gap-4">
              <div
                className="w-24 h-24 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: 'var(--bg-hover)' }}
              >
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <Button variant="outline">Upload Logo</Button>
            </div>
          </div>

          <Select
            label={t('settings.organization.defaultRole')}
            options={roleOptions}
            value="user"
            onChange={() => {}}
          />

          <div className="flex justify-end">
            <Button>{t('common.save')}</Button>
          </div>
        </CardBody>
      </Card>

      {/* SSO Configuration */}
      <Card>
        <CardHeader
          title={t('settings.organization.sso')}
          action={
            <div className="flex items-center gap-2">
              <Badge variant={ssoEnabled ? 'success' : 'secondary'}>
                {ssoEnabled ? t('settings.organization.ssoEnabled') : t('settings.organization.ssoDisabled')}
              </Badge>
              <Toggle checked={ssoEnabled} onChange={(checked) => setSsoEnabled(checked)} />
            </div>
          }
        />
        <CardBody>
          {ssoEnabled ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p style={{ color: 'var(--text-secondary)' }}>
                  Configure SAML 2.0 identity providers for single sign-on
                </p>
                <Button variant="outline" onClick={() => setShowAddProviderModal(true)}>
                  {t('settings.organization.addProvider')}
                </Button>
              </div>

              {providers.length === 0 ? (
                <div
                  className="text-center py-8 rounded-lg"
                  style={{ backgroundColor: 'var(--bg-hover)' }}
                >
                  <p style={{ color: 'var(--text-secondary)' }}>
                    No SSO providers configured yet
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {providers.map((provider) => (
                    <div
                      key={provider.id}
                      className="flex items-center justify-between p-4 rounded-lg"
                      style={{ backgroundColor: 'var(--bg-hover)' }}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: 'var(--bg-card)' }}
                        >
                          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                            {provider.name}
                          </p>
                          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                            {provider.type}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Toggle
                          checked={provider.isActive}
                          onChange={() => toggleProviderStatus(provider.id)}
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteProvider(provider.id)}
                        >
                          <svg className="w-4 h-4 text-error-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <Alert variant="info">
              Enable SSO to configure SAML 2.0 identity providers for your organization.
            </Alert>
          )}
        </CardBody>
      </Card>

      {/* Add Provider Modal */}
      <Modal
        isOpen={showAddProviderModal}
        onClose={() => setShowAddProviderModal(false)}
        title={t('settings.organization.addProvider')}
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowAddProviderModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleAddProvider}>
              {t('common.create')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('settings.organization.providerName')}
            value={newProvider.name}
            onChange={(e) => setNewProvider((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., Okta, Azure AD"
          />
          <Input
            label={t('settings.organization.entityId')}
            value={newProvider.entityId}
            onChange={(e) => setNewProvider((prev) => ({ ...prev, entityId: e.target.value }))}
            placeholder="https://idp.example.com/entity-id"
          />
          <Input
            label={t('settings.organization.ssoUrl')}
            value={newProvider.ssoUrl}
            onChange={(e) => setNewProvider((prev) => ({ ...prev, ssoUrl: e.target.value }))}
            placeholder="https://idp.example.com/sso"
          />
          <div>
            <label className="label">{t('settings.organization.certificate')}</label>
            <textarea
              className="input min-h-32"
              value={newProvider.certificate}
              onChange={(e) => setNewProvider((prev) => ({ ...prev, certificate: e.target.value }))}
              placeholder="Paste X.509 certificate here..."
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default OrganizationSettings;
