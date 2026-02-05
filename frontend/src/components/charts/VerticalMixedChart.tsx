import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface VerticalMixedChartProps {
  title: string;
  height?: number;
}

export const VerticalMixedChart: React.FC<VerticalMixedChartProps> = ({
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
      data: ['Sales', 'Orders', 'Growth Rate'],
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
    yAxis: [
      {
        type: 'value',
        name: 'Amount',
        position: 'left',
        axisLabel: { color: '#666', formatter: '${value}k' },
      },
      {
        type: 'value',
        name: 'Growth %',
        position: 'right',
        axisLabel: { color: '#666', formatter: '{value}%' },
        max: 50,
        min: -10,
      },
    ],
    series: [
      {
        name: 'Sales',
        type: 'bar',
        data: [220, 182, 191, 234, 290, 330, 310, 280, 295, 340, 380, 410],
        itemStyle: { color: '#3B82F6' },
      },
      {
        name: 'Orders',
        type: 'bar',
        data: [150, 132, 141, 174, 210, 260, 250, 220, 235, 280, 310, 340],
        itemStyle: { color: '#10B981' },
      },
      {
        name: 'Growth Rate',
        type: 'line',
        yAxisIndex: 1,
        data: [12, -5, 8, 22, 24, 14, -6, -10, 5, 15, 12, 8],
        smooth: true,
        lineStyle: { color: '#8B5CF6', width: 3 },
        itemStyle: { color: '#8B5CF6' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0)' },
            ],
          },
        },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default VerticalMixedChart;
