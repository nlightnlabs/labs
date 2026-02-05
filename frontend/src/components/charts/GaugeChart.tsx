import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface GaugeChartProps {
  title: string;
  value?: number;
  height?: number;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  title,
  value = 72.5,
  height = 300,
}) => {
  const option: EChartsOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        center: ['50%', '75%'],
        radius: '100%',
        min: 0,
        max: 100,
        splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 6,
            color: [
              [0.3, '#EF4444'],
              [0.7, '#F59E0B'],
              [1, '#10B981'],
            ],
          },
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '12%',
          width: 20,
          offsetCenter: [0, '-60%'],
          itemStyle: {
            color: 'auto',
          },
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2,
          },
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 5,
          },
        },
        axisLabel: {
          color: '#666',
          fontSize: 12,
          distance: -60,
          rotate: 'tangential',
          formatter: (value: number) => {
            if (value === 0) return 'Low';
            if (value === 50) return 'Medium';
            if (value === 100) return 'High';
            return '';
          },
        },
        title: {
          offsetCenter: [0, '-10%'],
          fontSize: 16,
          color: '#666',
        },
        detail: {
          fontSize: 32,
          offsetCenter: [0, '-35%'],
          valueAnimation: true,
          formatter: (val: number) => `${val.toFixed(1)}%`,
          color: 'inherit',
        },
        data: [
          {
            value,
            name: 'Performance',
          },
        ],
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default GaugeChart;
