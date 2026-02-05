import React from 'react';
import { useTranslation } from 'react-i18next';
import { Avatar, Badge } from '@/components/common';
import { ActivityItem } from '@/types';

// Mock activity data - in production this would come from API
const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'user_created',
    description: 'New user John Doe registered',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    metadata: { userName: 'John Doe' },
  },
  {
    id: '2',
    type: 'settings_updated',
    description: 'Organization settings updated',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    metadata: { setting: 'SSO Configuration' },
  },
  {
    id: '3',
    type: 'login',
    description: 'User Jane Smith logged in',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
    metadata: { userName: 'Jane Smith' },
  },
  {
    id: '4',
    type: 'api_key_created',
    description: 'New API key generated',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    metadata: { keyName: 'Production API' },
  },
  {
    id: '5',
    type: 'password_changed',
    description: 'User Bob Wilson changed password',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    metadata: { userName: 'Bob Wilson' },
  },
];

const activityIcons: Record<string, { icon: React.ReactNode; color: string }> = {
  user_created: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
      </svg>
    ),
    color: 'bg-success-100 text-success-600',
  },
  settings_updated: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    color: 'bg-info-100 text-info-600',
  },
  login: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
      </svg>
    ),
    color: 'bg-primary-100 text-primary-600',
  },
  api_key_created: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    color: 'bg-warning-100 text-warning-600',
  },
  password_changed: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    color: 'bg-secondary-100 text-secondary-600',
  },
};

const formatRelativeTime = (timestamp: string): string => {
  const now = new Date();
  const date = new Date(timestamp);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else {
    return `${diffDays}d ago`;
  }
};

export const ActivityFeed: React.FC = () => {
  const { t } = useTranslation();

  if (mockActivities.length === 0) {
    return (
      <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
        {t('dashboard.noActivity')}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {mockActivities.map((activity) => {
        const iconConfig = activityIcons[activity.type] || activityIcons.login;

        return (
          <div key={activity.id} className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${iconConfig.color}`}>
              {iconConfig.icon}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm" style={{ color: 'var(--text-primary)' }}>
                {activity.description}
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                {formatRelativeTime(activity.timestamp)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ActivityFeed;
