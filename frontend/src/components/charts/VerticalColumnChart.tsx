import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface VerticalColumnChartProps {
  title: string;
  categories?: string[];
  series?: { name: string; data: number[] }[];
  height?: number;
}

export const VerticalColumnChart: React.FC<VerticalColumnChartProps> = ({
  title,
  categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  series = [
    { name: 'Product A', data: [120, 200, 150, 80, 70, 110] },
    { name: 'Product B', data: [60, 80, 70, 110, 130, 150] },
    { name: 'Product C', data: [90, 110, 100, 70, 50, 80] },
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
      data: s.data,
      itemStyle: { color: colors[index % colors.length] },
    })),
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default VerticalColumnChart;
