import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HorizontalMixedChartProps {
  title: string;
  height?: number;
}

export const HorizontalMixedChart: React.FC<HorizontalMixedChartProps> = ({
  title,
  height = 300,
}) => {
  const categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: ['Revenue', 'Expenses', 'Profit Margin'],
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
    xAxis: [
      {
        type: 'value',
        position: 'bottom',
        axisLabel: { color: '#666', formatter: '${value}k' },
      },
      {
        type: 'value',
        position: 'top',
        axisLabel: { color: '#666', formatter: '{value}%' },
        max: 100,
        min: 0,
      },
    ],
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#666' },
    },
    series: [
      {
        name: 'Revenue',
        type: 'bar',
        data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330],
        itemStyle: { color: '#3B82F6' },
      },
      {
        name: 'Expenses',
        type: 'bar',
        data: [80, 92, 71, 94, 60, 130, 110, 102, 111, 134, 170, 180],
        itemStyle: { color: '#EF4444' },
      },
      {
        name: 'Profit Margin',
        type: 'line',
        xAxisIndex: 1,
        data: [33, 30, 30, 30, 33, 43, 48, 44, 42, 43, 41, 45],
        smooth: true,
        lineStyle: { color: '#10B981', width: 3 },
        itemStyle: { color: '#10B981' },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default HorizontalMixedChart;
