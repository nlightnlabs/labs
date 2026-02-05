import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ActionsPageProps {
  appName: string;
}

const mockActions = [
  {
    id: 1,
    name: 'Export Data Report',
    description: 'Generate and download a comprehensive data report in CSV or PDF format.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    color: 'blue',
    status: 'ready',
  },
  {
    id: 2,
    name: 'Send Notifications',
    description: 'Send bulk notifications to selected user segments via email or push.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    color: 'purple',
    status: 'ready',
  },
  {
    id: 3,
    name: 'Sync External Data',
    description: 'Synchronize data with connected external services and APIs.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    color: 'green',
    status: 'running',
  },
  {
    id: 4,
    name: 'Generate Analytics',
    description: 'Run advanced analytics and machine learning models on your data.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    color: 'orange',
    status: 'ready',
  },
  {
    id: 5,
    name: 'Archive Old Records',
    description: 'Move old records to archive storage to improve performance.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
      </svg>
    ),
    color: 'gray',
    status: 'ready',
  },
  {
    id: 6,
    name: 'Schedule Report',
    description: 'Set up automated report generation on a daily, weekly, or monthly basis.',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    color: 'indigo',
    status: 'scheduled',
  },
];

const colorStyles: Record<string, { bg: string; icon: string }> = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    icon: 'bg-blue-100 text-blue-600 dark:bg-blue-800 dark:text-blue-400',
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    icon: 'bg-purple-100 text-purple-600 dark:bg-purple-800 dark:text-purple-400',
  },
  green: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    icon: 'bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-400',
  },
  orange: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    icon: 'bg-orange-100 text-orange-600 dark:bg-orange-800 dark:text-orange-400',
  },
  gray: {
    bg: 'bg-gray-50 dark:bg-gray-800/50',
    icon: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
  },
  indigo: {
    bg: 'bg-indigo-50 dark:bg-indigo-900/20',
    icon: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-800 dark:text-indigo-400',
  },
};

const statusBadges: Record<string, { bg: string; text: string }> = {
  ready: { bg: 'bg-green-100 dark:bg-green-800', text: 'text-green-800 dark:text-green-200' },
  running: { bg: 'bg-blue-100 dark:bg-blue-800', text: 'text-blue-800 dark:text-blue-200' },
  scheduled: { bg: 'bg-purple-100 dark:bg-purple-800', text: 'text-purple-800 dark:text-purple-200' },
};

export const ActionsPage: React.FC<ActionsPageProps> = ({ appName }) => {
  const { t } = useTranslation();
  const [runningActions, setRunningActions] = useState<number[]>([3]); // Action 3 is initially running

  const handleRunAction = (actionId: number) => {
    if (runningActions.includes(actionId)) return;
    setRunningActions((prev) => [...prev, actionId]);
    // Simulate action completion
    setTimeout(() => {
      setRunningActions((prev) => prev.filter((id) => id !== actionId));
    }, 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('modules.actions.title')}
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {t('modules.actions.description')}
        </p>
      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockActions.map((action) => {
          const styles = colorStyles[action.color] || colorStyles.gray;
          const isRunning = runningActions.includes(action.id);
          const status = isRunning ? 'running' : action.status;
          const badge = statusBadges[status] || statusBadges.ready;

          return (
            <div
              key={action.id}
              className="rounded-xl p-5 border transition-shadow hover:shadow-md"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-default)',
              }}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${styles.icon}`}>{action.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
                      {action.name}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                    {action.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${badge.bg} ${badge.text}`}>
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </span>
                    <button
                      onClick={() => handleRunAction(action.id)}
                      disabled={isRunning}
                      className={`btn btn-sm ${isRunning ? 'btn-outline opacity-50' : 'btn-primary'}`}
                    >
                      {isRunning ? (
                        <span className="flex items-center gap-2">
                          <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          Running
                        </span>
                      ) : (
                        'Run'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ActionsPage;
