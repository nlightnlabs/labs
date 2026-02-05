import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface ScatterChartProps {
  title: string;
  height?: number;
}

// Generate sample data with weight (size)
const generateData = () => {
  const data: [number, number, number][] = [];
  for (let i = 0; i < 50; i++) {
    data.push([
      Math.random() * 100,
      Math.random() * 100,
      Math.random() * 50 + 10,
    ]);
  }
  return data;
};

export const ScatterChart: React.FC<ScatterChartProps> = ({
  title,
  height = 300,
}) => {
  const data1 = generateData();
  const data2 = generateData();

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.seriesName}<br/>X: ${params.value[0].toFixed(1)}<br/>Y: ${params.value[1].toFixed(1)}<br/>Size: ${params.value[2].toFixed(1)}`;
      },
    },
    legend: {
      data: ['Group A', 'Group B'],
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
      splitLine: {
        lineStyle: { type: 'dashed', color: '#eee' },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
      splitLine: {
        lineStyle: { type: 'dashed', color: '#eee' },
      },
    },
    series: [
      {
        name: 'Group A',
        type: 'scatter',
        data: data1,
        symbolSize: (data: number[]) => data[2] / 2,
        itemStyle: {
          color: '#3B82F6',
          opacity: 0.7,
        },
        emphasis: {
          itemStyle: {
            opacity: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(59, 130, 246, 0.5)',
          },
        },
      },
      {
        name: 'Group B',
        type: 'scatter',
        data: data2,
        symbolSize: (data: number[]) => data[2] / 2,
        itemStyle: {
          color: '#10B981',
          opacity: 0.7,
        },
        emphasis: {
          itemStyle: {
            opacity: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(16, 185, 129, 0.5)',
          },
        },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default ScatterChart;
