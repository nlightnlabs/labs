import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HeatmapChartProps {
  title: string;
  height?: number;
}

export const HeatmapChart: React.FC<HeatmapChartProps> = ({
  title,
  height = 300,
}) => {
  const hours = ['12a', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12p', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p'];
  const days = ['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'];

  // Generate random data
  const data: [number, number, number][] = [];
  for (let i = 0; i < 7; i++) {
    for (let j = 0; j < 24; j++) {
      data.push([j, i, Math.floor(Math.random() * 100)]);
    }
  }

  const option: EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${days[params.value[1]]} ${hours[params.value[0]]}: ${params.value[2]}`;
      },
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '5%',
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: true },
      axisLabel: {
        color: '#666',
        fontSize: 10,
        interval: 2,
      },
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: { show: true },
      axisLabel: { color: '#666' },
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#EF4444', '#F59E0B', '#10B981'],
      },
      textStyle: { color: '#666' },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: { show: false },
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

export default HeatmapChart;
