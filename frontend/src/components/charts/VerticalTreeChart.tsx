import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface VerticalTreeChartProps {
  title: string;
  height?: number;
}

export const VerticalTreeChart: React.FC<VerticalTreeChartProps> = ({
  title,
  height = 350,
}) => {
  const data = {
    name: 'CEO',
    children: [
      {
        name: 'CTO',
        children: [
          { name: 'VP Engineering' },
          { name: 'VP Product' },
        ],
      },
      {
        name: 'CFO',
        children: [
          { name: 'Controller' },
          { name: 'Treasurer' },
        ],
      },
      {
        name: 'COO',
        children: [
          { name: 'VP Operations' },
          { name: 'VP Sales' },
          { name: 'VP Marketing' },
        ],
      },
    ],
  };

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
    },
    series: [
      {
        type: 'tree',
        data: [data],
        top: '5%',
        left: '10%',
        bottom: '5%',
        right: '10%',
        symbol: 'roundRect',
        symbolSize: [60, 30],
        orient: 'TB',
        expandAndCollapse: true,
        initialTreeDepth: 3,
        label: {
          position: 'inside',
          verticalAlign: 'middle',
          align: 'center',
          fontSize: 10,
          color: '#fff',
        },
        lineStyle: {
          color: '#ccc',
          width: 1.5,
        },
        itemStyle: {
          color: '#3B82F6',
          borderColor: '#1D4ED8',
          borderWidth: 1,
        },
        emphasis: {
          focus: 'descendant',
          itemStyle: {
            color: '#1D4ED8',
          },
        },
        animationDurationUpdate: 750,
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default VerticalTreeChart;
