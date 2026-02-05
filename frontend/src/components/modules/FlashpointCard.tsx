import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';

interface FlashpointCardProps {
  headline: string;
  insights: string[];
  recommendations: string[];
  chartData?: {
    categories: string[];
    barData: number[];
    lineData: number[];
    barName?: string;
    lineName?: string;
  };
  accentColor?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const accentColors = {
  blue: { primary: '#3B82F6', light: '#DBEAFE', dark: '#1D4ED8' },
  green: { primary: '#10B981', light: '#D1FAE5', dark: '#047857' },
  purple: { primary: '#8B5CF6', light: '#EDE9FE', dark: '#6D28D9' },
  orange: { primary: '#F59E0B', light: '#FEF3C7', dark: '#D97706' },
  red: { primary: '#EF4444', light: '#FEE2E2', dark: '#DC2626' },
};

export const FlashpointCard: React.FC<FlashpointCardProps> = ({
  headline,
  insights,
  recommendations,
  chartData = {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    barData: [120, 200, 150, 80, 70, 110],
    lineData: [30, 45, 35, 50, 40, 60],
    barName: 'Volume',
    lineName: 'Growth %',
  },
  accentColor = 'blue',
}) => {
  const colors = accentColors[accentColor];

  const chartOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: [chartData.barName || 'Volume', chartData.lineName || 'Trend'],
      top: 0,
      textStyle: { color: '#666', fontSize: 11 },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: chartData.categories,
      axisLabel: { color: '#666', fontSize: 10 },
      axisLine: { lineStyle: { color: '#E5E7EB' } },
    },
    yAxis: [
      {
        type: 'value',
        name: chartData.barName || 'Volume',
        position: 'left',
        axisLabel: { color: '#666', fontSize: 10 },
        axisLine: { lineStyle: { color: '#E5E7EB' } },
        splitLine: { lineStyle: { color: '#F3F4F6' } },
      },
      {
        type: 'value',
        name: chartData.lineName || 'Trend',
        position: 'right',
        axisLabel: { color: '#666', fontSize: 10, formatter: '{value}%' },
        axisLine: { lineStyle: { color: '#E5E7EB' } },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: chartData.barName || 'Volume',
        type: 'bar',
        data: chartData.barData,
        itemStyle: { color: colors.primary, borderRadius: [4, 4, 0, 0] },
        barWidth: '60%',
      },
      {
        name: chartData.lineName || 'Trend',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.lineData,
        smooth: true,
        lineStyle: { color: colors.dark, width: 3 },
        itemStyle: { color: colors.dark },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: `${colors.primary}40` },
              { offset: 1, color: `${colors.primary}00` },
            ],
          },
        },
      },
    ],
  };

  return (
    <div
      className="rounded-xl overflow-hidden transition-shadow hover:shadow-lg"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      {/* Headline Section */}
      <div
        className="px-6 py-4 border-b"
        style={{
          borderColor: 'var(--border-default)',
          background: `linear-gradient(135deg, ${colors.light}50, transparent)`,
        }}
      >
        <h2
          className="text-xl md:text-2xl font-bold"
          style={{ color: colors.dark }}
        >
          {headline}
        </h2>
      </div>

      {/* Content Section */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart Section - Left */}
          <div className="min-h-[280px]">
            <ReactECharts
              option={chartOption}
              style={{ height: '280px', width: '100%' }}
              opts={{ renderer: 'svg' }}
            />
          </div>

          {/* Insights & Recommendations - Right */}
          <div className="space-y-6">
            {/* Key Insights */}
            <div>
              <h3
                className="text-sm font-semibold uppercase tracking-wide mb-3 flex items-center gap-2"
                style={{ color: colors.primary }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Key Insights
              </h3>
              <ul className="space-y-2">
                {insights.map((insight, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    <span
                      className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium mt-0.5"
                      style={{ backgroundColor: colors.light, color: colors.dark }}
                    >
                      {index + 1}
                    </span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div>
              <h3
                className="text-sm font-semibold uppercase tracking-wide mb-3 flex items-center gap-2"
                style={{ color: colors.primary }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recommendations
              </h3>
              <ul className="space-y-2">
                {recommendations.map((rec, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    <svg
                      className="w-4 h-4 flex-shrink-0 mt-0.5"
                      style={{ color: colors.primary }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlashpointCard;
