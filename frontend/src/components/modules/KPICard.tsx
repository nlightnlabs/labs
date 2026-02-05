import React from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

const colorStyles = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    icon: 'bg-blue-100 text-blue-600 dark:bg-blue-800 dark:text-blue-400',
  },
  green: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    icon: 'bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-400',
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    icon: 'bg-purple-100 text-purple-600 dark:bg-purple-800 dark:text-purple-400',
  },
  orange: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    icon: 'bg-orange-100 text-orange-600 dark:bg-orange-800 dark:text-orange-400',
  },
};

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon,
  color = 'blue',
}) => {
  const styles = colorStyles[color];
  const isPositiveChange = change !== undefined && change >= 0;

  return (
    <div
      className="rounded-xl p-5 transition-shadow hover:shadow-md"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-2 text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            {value}
          </p>
          {change !== undefined && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={`text-sm font-medium ${
                  isPositiveChange ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                }`}
              >
                {isPositiveChange ? '+' : ''}
                {change}%
              </span>
              {changeLabel && (
                <span className="text-sm text-gray-500 dark:text-gray-400">{changeLabel}</span>
              )}
            </div>
          )}
        </div>
        {icon && (
          <div className={`p-3 rounded-xl ${styles.icon}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

export default KPICard;
