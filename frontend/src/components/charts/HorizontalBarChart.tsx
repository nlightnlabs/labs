import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HorizontalBarChartProps {
  title: string;
  categories?: string[];
  series?: { name: string; data: number[] }[];
  height?: number;
}

export const HorizontalBarChart: React.FC<HorizontalBarChartProps> = ({
  title,
  categories = ['Brazil', 'Indonesia', 'USA', 'India', 'China', 'World'],
  series = [
    { name: '2023', data: [18203, 23489, 29034, 104970, 131744, 630230] },
    { name: '2024', data: [19325, 26578, 31456, 112890, 145678, 695420] },
  ],
  height = 300,
}) => {
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
      boundaryGap: [0, 0.01],
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
      data: s.data,
      itemStyle: {
        color: ['#3B82F6', '#10B981', '#8B5CF6'][index % 3],
      },
    })),
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default HorizontalBarChart;
