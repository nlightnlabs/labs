import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface CorrelationMatrixChartProps {
  title: string;
  height?: number;
}

export const CorrelationMatrixChart: React.FC<CorrelationMatrixChartProps> = ({
  title,
  height = 350,
}) => {
  const variables = ['Revenue', 'Users', 'Sessions', 'Conversion', 'Bounce Rate', 'Page Views'];

  // Generate correlation matrix data
  // Format: [x, y, correlation value]
  const data: [number, number, number][] = [];
  const correlationMatrix = [
    [1.00, 0.85, 0.78, 0.65, -0.42, 0.72],
    [0.85, 1.00, 0.92, 0.58, -0.35, 0.88],
    [0.78, 0.92, 1.00, 0.52, -0.48, 0.95],
    [0.65, 0.58, 0.52, 1.00, -0.68, 0.45],
    [-0.42, -0.35, -0.48, -0.68, 1.00, -0.55],
    [0.72, 0.88, 0.95, 0.45, -0.55, 1.00],
  ];

  for (let i = 0; i < variables.length; i++) {
    for (let j = 0; j < variables.length; j++) {
      data.push([j, i, correlationMatrix[i][j]]);
    }
  }

  const option: EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const val = params.value[2].toFixed(2);
        return `${variables[params.value[1]]} vs ${variables[params.value[0]]}<br/>Correlation: ${val}`;
      },
    },
    grid: {
      left: '15%',
      right: '12%',
      bottom: '15%',
      top: '5%',
    },
    xAxis: {
      type: 'category',
      data: variables,
      splitArea: { show: true },
      axisLabel: {
        color: '#666',
        fontSize: 10,
        rotate: 45,
      },
    },
    yAxis: {
      type: 'category',
      data: variables,
      splitArea: { show: true },
      axisLabel: {
        color: '#666',
        fontSize: 10,
      },
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'vertical',
      right: '2%',
      top: 'center',
      inRange: {
        color: ['#3B82F6', '#FFFFFF', '#EF4444'],
      },
      textStyle: { color: '#666' },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: true,
          formatter: (params: any) => params.value[2].toFixed(2),
          fontSize: 9,
          color: '#333',
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default CorrelationMatrixChart;
