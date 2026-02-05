import React from 'react';
import { useTranslation } from 'react-i18next';
import { KPICard } from '@/components/modules';
import {
  PieChart,
  DoughnutChart,
  GaugeChart,
  HorizontalBarChart,
  HorizontalStackedBarChart,
  HorizontalMixedChart,
  VerticalColumnChart,
  VerticalStackedColumnChart,
  VerticalMixedChart,
  ScatterChart,
  CandlestickChart,
  HorizontalCandlestickChart,
  HeatmapChart,
  TreemapChart,
  HorizontalTreeChart,
  VerticalTreeChart,
  GraphChart,
  CorrelationMatrixChart,
} from '@/components/charts';

interface SummaryPageProps {
  appName: string;
}

// Mock data for KPIs
const kpiData = [
  {
    id: 'revenue',
    titleKey: 'modules.kpi.totalRevenue',
    value: '$124,592',
    change: 12.5,
    changeLabel: 'vs last month',
    color: 'blue' as const,
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    id: 'users',
    titleKey: 'modules.kpi.activeUsers',
    value: '8,429',
    change: 8.2,
    changeLabel: 'vs last month',
    color: 'green' as const,
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
  {
    id: 'conversion',
    titleKey: 'modules.kpi.conversionRate',
    value: '3.24%',
    change: -2.1,
    changeLabel: 'vs last month',
    color: 'purple' as const,
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    id: 'session',
    titleKey: 'modules.kpi.avgSessionTime',
    value: '4m 32s',
    change: 5.7,
    changeLabel: 'vs last month',
    color: 'orange' as const,
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
];

// Chart configurations
const chartConfigs = [
  { id: 'pie', title: 'Pie Chart - Traffic Sources', Component: PieChart },
  { id: 'doughnut', title: 'Doughnut Chart - Device Distribution', Component: DoughnutChart },
  { id: 'gauge', title: 'Gauge Chart - Performance Score', Component: GaugeChart },
  { id: 'hbar', title: 'Horizontal Bar Chart - Country Revenue', Component: HorizontalBarChart },
  { id: 'hstacked', title: 'Horizontal Stacked Bar - Channel Mix', Component: HorizontalStackedBarChart },
  { id: 'hmixed', title: 'Horizontal Mixed - Revenue & Profit Margin', Component: HorizontalMixedChart },
  { id: 'vcol', title: 'Vertical Column Chart - Product Sales', Component: VerticalColumnChart },
  { id: 'vstacked', title: 'Vertical Stacked Column - Regional Sales', Component: VerticalStackedColumnChart },
  { id: 'vmixed', title: 'Vertical Mixed - Sales & Growth Rate', Component: VerticalMixedChart },
  { id: 'scatter', title: 'Scatter Plot - Customer Segments', Component: ScatterChart },
  { id: 'candle', title: 'Candlestick Chart - Stock Prices', Component: CandlestickChart },
  { id: 'hcandle', title: 'Box Plot - Category Distribution', Component: HorizontalCandlestickChart },
  { id: 'heatmap', title: 'Heatmap - Activity by Hour', Component: HeatmapChart },
  { id: 'treemap', title: 'Treemap - Industry Breakdown', Component: TreemapChart },
  { id: 'htree', title: 'Horizontal Tree - Organization Structure', Component: HorizontalTreeChart },
  { id: 'vtree', title: 'Vertical Tree - Hierarchy', Component: VerticalTreeChart },
  { id: 'graph', title: 'Network Graph - Relationships', Component: GraphChart },
  { id: 'corr', title: 'Correlation Matrix - Metrics', Component: CorrelationMatrixChart },
];

export const SummaryPage: React.FC<SummaryPageProps> = ({ appName }) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* KPI Cards Section */}
      <section>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiData.map((kpi) => (
            <KPICard
              key={kpi.id}
              title={t(kpi.titleKey)}
              value={kpi.value}
              change={kpi.change}
              changeLabel={kpi.changeLabel}
              icon={kpi.icon}
              color={kpi.color}
            />
          ))}
        </div>
      </section>

      {/* Charts Section with Infinite Scroll Container */}
      <section>
        <div className="mb-4">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
            Analytics Charts
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Scroll to view all chart types
          </p>
        </div>

        {/* Scrollable Chart Container */}
        <div
          className="overflow-y-auto pr-2 scrollbar-thin"
          style={{
            maxHeight: 'calc(100vh - 400px)',
            minHeight: '500px',
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-4">
            {chartConfigs.map(({ id, title, Component }) => (
              <Component key={id} title={title} height={280} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default SummaryPage;
