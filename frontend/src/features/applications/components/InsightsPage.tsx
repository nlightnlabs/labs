import React from 'react';
import { useTranslation } from 'react-i18next';
import { FlashpointCard } from '@/components/modules';

interface InsightsPageProps {
  appName: string;
}

// Flashpoint data for different insight categories
const flashpointData = [
  {
    id: 'revenue',
    headline: 'Revenue Growth Accelerating This Quarter',
    accentColor: 'green' as const,
    chartData: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      barData: [85, 92, 98, 105, 118, 132],
      lineData: [8, 12, 15, 18, 22, 28],
      barName: 'Revenue ($K)',
      lineName: 'Growth %',
    },
    insights: [
      'Revenue increased 28% compared to same period last year',
      'Subscription revenue now accounts for 65% of total revenue',
      'Enterprise segment showing strongest growth at 42% YoY',
      'Customer lifetime value increased by $2,400 on average',
    ],
    recommendations: [
      'Invest more in enterprise sales team to capitalize on momentum',
      'Consider launching annual subscription incentives to boost retention',
      'Expand marketing spend in high-performing regions',
      'Develop case studies from top enterprise customers',
    ],
  },
  {
    id: 'engagement',
    headline: 'User Engagement Peaks in Afternoon Hours',
    accentColor: 'blue' as const,
    chartData: {
      categories: ['6am', '9am', '12pm', '3pm', '6pm', '9pm'],
      barData: [120, 450, 680, 890, 720, 340],
      lineData: [2, 8, 12, 18, 14, 6],
      barName: 'Active Users',
      lineName: 'Engagement Score',
    },
    insights: [
      'Peak engagement occurs between 2pm-5pm across all time zones',
      'Mobile users show 40% higher engagement than desktop',
      'Average session duration increased to 8.5 minutes',
      'Feature adoption rate improved by 25% after recent UX updates',
    ],
    recommendations: [
      'Schedule important notifications during peak engagement hours',
      'Prioritize mobile-first design for new features',
      'Implement gamification elements to extend session duration',
      'A/B test onboarding flows to improve feature discovery',
    ],
  },
  {
    id: 'conversion',
    headline: 'Conversion Funnel Shows Optimization Opportunities',
    accentColor: 'purple' as const,
    chartData: {
      categories: ['Visit', 'Signup', 'Activate', 'Convert', 'Retain', 'Expand'],
      barData: [10000, 3200, 1800, 720, 580, 290],
      lineData: [100, 32, 18, 7.2, 5.8, 2.9],
      barName: 'Users',
      lineName: 'Conversion %',
    },
    insights: [
      'Biggest drop-off occurs between signup and activation (44% loss)',
      'Users who complete onboarding are 3x more likely to convert',
      'Email verification step causing 18% abandonment',
      'Free trial to paid conversion improved to 40% (up from 32%)',
    ],
    recommendations: [
      'Simplify onboarding to 3 steps or fewer',
      'Implement social login to reduce signup friction',
      'Add progress indicators during activation flow',
      'Create targeted re-engagement campaigns for inactive signups',
    ],
  },
  {
    id: 'performance',
    headline: 'System Performance Exceeds SLA Targets',
    accentColor: 'orange' as const,
    chartData: {
      categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
      barData: [99.2, 99.5, 99.8, 99.9, 99.7, 99.95],
      lineData: [180, 165, 142, 128, 135, 118],
      barName: 'Uptime %',
      lineName: 'Latency (ms)',
    },
    insights: [
      'Average uptime maintained at 99.7% over past 6 weeks',
      'API response time reduced by 35% after CDN optimization',
      'Zero critical incidents reported in the last 30 days',
      'Database query performance improved by 50% with new indexes',
    ],
    recommendations: [
      'Continue monitoring for any latency regressions',
      'Plan capacity expansion before Q4 traffic surge',
      'Implement additional caching layers for read-heavy endpoints',
      'Schedule regular load testing to validate scalability',
    ],
  },
  {
    id: 'churn',
    headline: 'Churn Risk Identified in SMB Segment',
    accentColor: 'red' as const,
    chartData: {
      categories: ['Startup', 'SMB', 'Mid-Market', 'Enterprise', 'Strategic'],
      barData: [120, 85, 45, 12, 3],
      lineData: [8, 12, 5, 2, 0.5],
      barName: 'At-Risk Accounts',
      lineName: 'Churn Rate %',
    },
    insights: [
      'SMB segment shows 12% churn rate, 4x higher than enterprise',
      '67% of churned customers cited lack of support as primary reason',
      'Customers with less than 3 integrations are 5x more likely to churn',
      'Price sensitivity increased among startups in current market',
    ],
    recommendations: [
      'Launch dedicated SMB success program with proactive outreach',
      'Create self-service resources to reduce support dependency',
      'Incentivize integration adoption with onboarding credits',
      'Consider flexible pricing tiers for startup segment',
    ],
  },
];

export const InsightsPage: React.FC<InsightsPageProps> = ({ appName }) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('modules.insights.title')}
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Key flashpoints and actionable recommendations based on your data
        </p>
      </div>

      {/* Flashpoint Cards */}
      <div className="space-y-6">
        {flashpointData.map((flashpoint) => (
          <FlashpointCard
            key={flashpoint.id}
            headline={flashpoint.headline}
            insights={flashpoint.insights}
            recommendations={flashpoint.recommendations}
            chartData={flashpoint.chartData}
            accentColor={flashpoint.accentColor}
          />
        ))}
      </div>
    </div>
  );
};

export default InsightsPage;
