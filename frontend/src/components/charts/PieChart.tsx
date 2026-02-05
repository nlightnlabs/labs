import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface PieChartProps {
  title: string;
  data?: { name: string; value: number }[];
  height?: number;
}

export const PieChart: React.FC<PieChartProps> = ({
  title,
  data = [
    { name: 'Search Engine', value: 1048 },
    { name: 'Direct', value: 735 },
    { name: 'Email', value: 580 },
    { name: 'Union Ads', value: 484 },
    { name: 'Video Ads', value: 300 },
  ],
  height = 300,
}) => {
  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#666' },
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        center: ['40%', '50%'],
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        label: {
          show: false,
        },
      },
    ],
    color: ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4'],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default PieChart;
