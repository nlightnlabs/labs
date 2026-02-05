import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface DoughnutChartProps {
  title: string;
  data?: { name: string; value: number }[];
  height?: number;
}

export const DoughnutChart: React.FC<DoughnutChartProps> = ({
  title,
  data = [
    { name: 'Desktop', value: 1048 },
    { name: 'Mobile', value: 735 },
    { name: 'Tablet', value: 580 },
    { name: 'Other', value: 300 },
  ],
  height = 300,
}) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);

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
    graphic: {
      type: 'text',
      left: '32%',
      top: '45%',
      style: {
        text: total.toLocaleString(),
        textAlign: 'center',
        fill: '#333',
        fontSize: 24,
        fontWeight: 'bold',
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
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
    color: ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default DoughnutChart;
