import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Select, Toggle, Button } from '@/components/common';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { setThemeMode } from '@/store/slices/themeSlice';
import { languages } from '@/i18n';
import { ThemeMode } from '@/types';

export const PreferencesSettings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const dispatch = useAppDispatch();
  const { mode: themeMode } = useAppSelector((state) => state.theme);

  const [notifications, setNotifications] = React.useState({
    email: true,
    inApp: true,
    marketing: false,
    security: true,
  });

  const themeOptions = [
    { value: 'light', label: t('settings.preferences.themeLight') },
    { value: 'dark', label: t('settings.preferences.themeDark') },
    { value: 'system', label: t('settings.preferences.themeSystem') },
  ];

  const languageOptions = languages.map((lang) => ({
    value: lang.code,
    label: `${lang.name} (${lang.nativeName})`,
  }));

  const handleThemeChange = (value: string) => {
    dispatch(setThemeMode(value as ThemeMode));
  };

  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value);
  };

  const handleNotificationToggle = (key: keyof typeof notifications) => {
    setNotifications((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="space-y-6">
      {/* Theme Settings */}
      <Card>
        <CardHeader
          title={t('settings.preferences.title')}
          subtitle={t('settings.preferences.subtitle')}
        />
        <CardBody className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Select
              label={t('settings.preferences.theme')}
              options={themeOptions}
              value={themeMode}
              onChange={handleThemeChange}
            />

            <Select
              label={t('settings.preferences.language')}
              options={languageOptions}
              value={i18n.language}
              onChange={handleLanguageChange}
            />
          </div>

          {/* Theme Preview */}
          <div>
            <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--text-primary)' }}>
              Theme Preview
            </h4>
            <div className="grid grid-cols-3 gap-3">
              {['light', 'dark', 'system'].map((theme) => (
                <button
                  key={theme}
                  onClick={() => handleThemeChange(theme)}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    themeMode === theme
                      ? 'border-primary-500'
                      : 'border-transparent hover:border-gray-300'
                  }`}
                  style={{ backgroundColor: 'var(--bg-hover)' }}
                >
                  <div
                    className={`w-full h-16 rounded-md mb-2 ${
                      theme === 'dark'
                        ? 'bg-gray-800'
                        : theme === 'light'
                        ? 'bg-white border border-gray-200'
                        : 'bg-gradient-to-r from-white to-gray-800'
                    }`}
                  />
                  <p className="text-xs font-medium capitalize" style={{ color: 'var(--text-primary)' }}>
                    {theme}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader title={t('settings.preferences.notifications')} />
        <CardBody className="space-y-4">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                {t('settings.preferences.emailNotifications')}
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Receive notifications via email
              </p>
            </div>
            <Toggle
              checked={notifications.email}
              onChange={() => handleNotificationToggle('email')}
            />
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                {t('settings.preferences.inAppNotifications')}
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Show notifications in the app
              </p>
            </div>
            <Toggle
              checked={notifications.inApp}
              onChange={() => handleNotificationToggle('inApp')}
            />
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                {t('settings.preferences.marketingEmails')}
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Receive updates about new features and promotions
              </p>
            </div>
            <Toggle
              checked={notifications.marketing}
              onChange={() => handleNotificationToggle('marketing')}
            />
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                {t('settings.preferences.securityAlerts')}
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Get notified about security-related events
              </p>
            </div>
            <Toggle
              checked={notifications.security}
              onChange={() => handleNotificationToggle('security')}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button>{t('common.save')}</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default PreferencesSettings;
