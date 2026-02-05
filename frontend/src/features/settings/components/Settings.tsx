import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs, TabPanel } from '@/components/common';
import { useAppSelector } from '@/store/hooks';
import { ProfileSettings } from './ProfileSettings';
import { AccountSettings } from './AccountSettings';
import { PreferencesSettings } from './PreferencesSettings';
import { OrganizationSettings } from './OrganizationSettings';

export const Settings: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAppSelector((state) => state.auth);

  const tabs = [
    { id: 'profile', label: t('settings.profile.title') },
    { id: 'account', label: t('settings.account.title') },
    { id: 'preferences', label: t('settings.preferences.title') },
    ...(user?.role === 'admin' ? [{ id: 'organization', label: t('settings.organization.title') }] : []),
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {t('settings.title')}
        </h1>
      </div>

      <Tabs tabs={tabs} defaultTab="profile">
        <TabPanel tabId="profile">
          <ProfileSettings />
        </TabPanel>
        <TabPanel tabId="account">
          <AccountSettings />
        </TabPanel>
        <TabPanel tabId="preferences">
          <PreferencesSettings />
        </TabPanel>
        {user?.role === 'admin' && (
          <TabPanel tabId="organization">
            <OrganizationSettings />
          </TabPanel>
        )}
      </Tabs>
    </div>
  );
};

export default Settings;
