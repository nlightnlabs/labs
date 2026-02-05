import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HorizontalStackedBarChartProps {
  title: string;
  categories?: string[];
  series?: { name: string; data: number[] }[];
  height?: number;
}

export const HorizontalStackedBarChart: React.FC<HorizontalStackedBarChartProps> = ({
  title,
  categories = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  series = [
    { name: 'Direct', data: [320, 302, 301, 334, 390, 330, 320] },
    { name: 'Mail Ad', data: [120, 132, 101, 134, 90, 230, 210] },
    { name: 'Affiliate', data: [220, 182, 191, 234, 290, 330, 310] },
    { name: 'Video', data: [150, 212, 201, 154, 190, 330, 410] },
  ],
  height = 300,
}) => {
  const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444'];

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: series.map((s) => s.name),
      top: 0,
      textStyle: { color: '#666' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#666' },
    },
    series: series.map((s, index) => ({
      name: s.name,
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: s.data,
      itemStyle: { color: colors[index % colors.length] },
    })),
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default HorizontalStackedBarChart;
