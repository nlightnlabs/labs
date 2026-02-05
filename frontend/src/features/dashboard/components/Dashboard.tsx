import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, Badge } from '@/components/common';
import { useAppSelector } from '@/store/hooks';
import { StatsCard } from './StatsCard';
import { ActivityFeed } from './ActivityFeed';
import { QuickActions } from './QuickActions';

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAppSelector((state) => state.auth);

  // Mock stats data - in production this would come from API
  const stats = [
    {
      id: 'users',
      label: t('dashboard.stats.totalUsers'),
      value: '1,234',
      change: '+12%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
    },
    {
      id: 'active',
      label: t('dashboard.stats.activeUsers'),
      value: '856',
      change: '+8%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      id: 'sessions',
      label: t('dashboard.stats.totalSessions'),
      value: '3,567',
      change: '+23%',
      changeType: 'positive' as const,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
    },
    {
      id: 'storage',
      label: t('dashboard.stats.storageUsed'),
      value: '45.2 GB',
      change: '+5%',
      changeType: 'neutral' as const,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {t('dashboard.welcome', { name: user?.firstName || 'User' })}
        </h1>
        <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
          {t('dashboard.welcomeMessage')}
        </p>
      </div>

      {/* Stats Cards */}
      <div>
        <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          {t('dashboard.quickStats')}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <StatsCard key={stat.id} {...stat} />
          ))}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Feed - Takes 2 columns */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader
              title={t('dashboard.recentActivity')}
              action={
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  {t('dashboard.viewAll')}
                </button>
              }
            />
            <ActivityFeed />
          </Card>
        </div>

        {/* Quick Actions - Takes 1 column */}
        <div>
          <Card>
            <CardHeader title={t('dashboard.quickActions')} />
            <QuickActions />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
