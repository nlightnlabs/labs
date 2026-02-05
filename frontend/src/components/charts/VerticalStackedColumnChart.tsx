import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface VerticalStackedColumnChartProps {
  title: string;
  categories?: string[];
  series?: { name: string; data: number[] }[];
  height?: number;
}

export const VerticalStackedColumnChart: React.FC<VerticalStackedColumnChartProps> = ({
  title,
  categories = ['Q1', 'Q2', 'Q3', 'Q4'],
  series = [
    { name: 'North', data: [320, 302, 341, 374] },
    { name: 'South', data: [220, 182, 191, 234] },
    { name: 'East', data: [150, 212, 201, 154] },
    { name: 'West', data: [120, 132, 101, 134] },
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
      type: 'category',
      data: categories,
      axisLabel: { color: '#666' },
    },
    yAxis: {
      type: 'value',
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

export default VerticalStackedColumnChart;
