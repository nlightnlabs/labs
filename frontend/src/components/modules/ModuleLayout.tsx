import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

interface ModuleLayoutProps {
  basePath: string;
  title: string;
}

export const ModuleLayout: React.FC<ModuleLayoutProps> = ({ basePath, title }) => {
  const { t } = useTranslation();
  const location = useLocation();

  const tabs = [
    { id: 'summary', label: t('modules.tabs.summary'), path: '' },
    { id: 'insights', label: t('modules.tabs.insights'), path: '/insights' },
    { id: 'data', label: t('modules.tabs.data'), path: '/data' },
    { id: 'actions', label: t('modules.tabs.actions'), path: '/actions' },
    { id: 'settings', label: t('modules.tabs.settings'), path: '/settings' },
  ];

  const isTabActive = (tabPath: string) => {
    const fullPath = `${basePath}${tabPath}`;
    if (tabPath === '') {
      return location.pathname === basePath || location.pathname === `${basePath}/`;
    }
    return location.pathname.startsWith(fullPath);
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {title}
        </h1>

        {/* Horizontal Tab Navigation */}
        <nav className="flex border-b" style={{ borderColor: 'var(--border-default)' }}>
          {tabs.map((tab) => (
            <NavLink
              key={tab.id}
              to={`${basePath}${tab.path}`}
              end={tab.path === ''}
              className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
                isTabActive(tab.path)
                  ? 'text-blue-600 border-blue-600 dark:text-blue-400 dark:border-blue-400'
                  : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        <Outlet />
      </div>
    </div>
  );
};

export default ModuleLayout;
