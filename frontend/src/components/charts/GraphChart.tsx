import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface GraphChartProps {
  title: string;
  height?: number;
}

export const GraphChart: React.FC<GraphChartProps> = ({
  title,
  height = 350,
}) => {
  const nodes = [
    { id: '0', name: 'Node A', symbolSize: 50, category: 0 },
    { id: '1', name: 'Node B', symbolSize: 40, category: 0 },
    { id: '2', name: 'Node C', symbolSize: 35, category: 1 },
    { id: '3', name: 'Node D', symbolSize: 30, category: 1 },
    { id: '4', name: 'Node E', symbolSize: 45, category: 2 },
    { id: '5', name: 'Node F', symbolSize: 25, category: 2 },
    { id: '6', name: 'Node G', symbolSize: 35, category: 0 },
    { id: '7', name: 'Node H', symbolSize: 30, category: 1 },
    { id: '8', name: 'Node I', symbolSize: 40, category: 2 },
    { id: '9', name: 'Node J', symbolSize: 28, category: 0 },
  ];

  const links = [
    { source: '0', target: '1', value: 10 },
    { source: '0', target: '2', value: 8 },
    { source: '0', target: '4', value: 12 },
    { source: '1', target: '3', value: 6 },
    { source: '1', target: '6', value: 7 },
    { source: '2', target: '3', value: 5 },
    { source: '2', target: '5', value: 4 },
    { source: '3', target: '7', value: 8 },
    { source: '4', target: '5', value: 9 },
    { source: '4', target: '8', value: 11 },
    { source: '5', target: '6', value: 3 },
    { source: '6', target: '9', value: 6 },
    { source: '7', target: '8', value: 7 },
    { source: '8', target: '9', value: 5 },
  ];

  const categories = [
    { name: 'Group A' },
    { name: 'Group B' },
    { name: 'Group C' },
  ];

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}: ${params.data.value}`;
        }
        return params.data.name;
      },
    },
    legend: {
      data: categories.map((c) => c.name),
      top: 0,
      textStyle: { color: '#666' },
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links,
        categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 10,
          color: '#666',
        },
        labelLayout: {
          hideOverlap: true,
        },
        force: {
          repulsion: 200,
          edgeLength: [50, 100],
        },
        lineStyle: {
          color: 'source',
          curveness: 0.1,
          opacity: 0.6,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4 },
        },
      },
    ],
    color: ['#3B82F6', '#10B981', '#8B5CF6'],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default GraphChart;
