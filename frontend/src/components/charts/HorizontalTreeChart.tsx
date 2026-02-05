import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface HorizontalTreeChartProps {
  title: string;
  height?: number;
}

export const HorizontalTreeChart: React.FC<HorizontalTreeChartProps> = ({
  title,
  height = 350,
}) => {
  const data = {
    name: 'Organization',
    children: [
      {
        name: 'Engineering',
        children: [
          {
            name: 'Frontend',
            children: [
              { name: 'React Team' },
              { name: 'Mobile Team' },
            ],
          },
          {
            name: 'Backend',
            children: [
              { name: 'API Team' },
              { name: 'Data Team' },
            ],
          },
          { name: 'DevOps' },
        ],
      },
      {
        name: 'Product',
        children: [
          { name: 'Design' },
          { name: 'Research' },
          { name: 'Analytics' },
        ],
      },
      {
        name: 'Operations',
        children: [
          { name: 'HR' },
          { name: 'Finance' },
          { name: 'Legal' },
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
        left: '2%',
        right: '2%',
        top: '8%',
        bottom: '20%',
        symbol: 'circle',
        symbolSize: 10,
        orient: 'LR',
        expandAndCollapse: true,
        initialTreeDepth: 3,
        label: {
          position: 'left',
          verticalAlign: 'middle',
          align: 'right',
          fontSize: 11,
          color: '#666',
        },
        leaves: {
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left',
          },
        },
        lineStyle: {
          color: '#ccc',
          width: 1.5,
        },
        itemStyle: {
          color: '#3B82F6',
          borderColor: '#3B82F6',
        },
        emphasis: {
          focus: 'descendant',
        },
        animationDurationUpdate: 750,
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default HorizontalTreeChart;
