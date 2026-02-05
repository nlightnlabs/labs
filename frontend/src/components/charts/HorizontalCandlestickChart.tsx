import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HorizontalCandlestickChartProps {
  title: string;
  height?: number;
}

export const HorizontalCandlestickChart: React.FC<HorizontalCandlestickChartProps> = ({
  title,
  height = 300,
}) => {
  // Aggregate data showing min, Q1, median, Q3, max for categories
  const categories = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Automotive'];

  // Data: [min, Q1, median, Q3, max]
  const data = [
    [50, 75, 120, 180, 250],
    [30, 55, 85, 125, 180],
    [20, 40, 60, 90, 130],
    [80, 110, 150, 200, 280],
    [100, 140, 190, 260, 350],
  ];

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const d = params.data;
        return `${params.name}<br/>Min: ${d[0]}<br/>Q1: ${d[1]}<br/>Median: ${d[2]}<br/>Q3: ${d[3]}<br/>Max: ${d[4]}`;
      },
    },
    grid: {
      left: '15%',
      right: '10%',
      bottom: '10%',
      top: '10%',
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
      splitLine: {
        lineStyle: { type: 'dashed', color: '#eee' },
      },
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#666' },
    },
    series: [
      {
        type: 'boxplot',
        data: data.map((item, idx) => ({
          name: categories[idx],
          value: item,
        })),
        itemStyle: {
          color: '#3B82F6',
          borderColor: '#1D4ED8',
        },
        emphasis: {
          itemStyle: {
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(59, 130, 246, 0.3)',
          },
        },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default HorizontalCandlestickChart;
