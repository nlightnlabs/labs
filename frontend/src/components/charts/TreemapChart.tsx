import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface TreemapChartProps {
  title: string;
  height?: number;
}

export const TreemapChart: React.FC<TreemapChartProps> = ({
  title,
  height = 300,
}) => {
  const data = [
    {
      name: 'Technology',
      value: 40,
      children: [
        { name: 'Software', value: 20 },
        { name: 'Hardware', value: 12 },
        { name: 'Services', value: 8 },
      ],
    },
    {
      name: 'Healthcare',
      value: 30,
      children: [
        { name: 'Pharma', value: 15 },
        { name: 'Biotech', value: 10 },
        { name: 'Equipment', value: 5 },
      ],
    },
    {
      name: 'Finance',
      value: 25,
      children: [
        { name: 'Banking', value: 12 },
        { name: 'Insurance', value: 8 },
        { name: 'Investment', value: 5 },
      ],
    },
    {
      name: 'Consumer',
      value: 20,
      children: [
        { name: 'Retail', value: 10 },
        { name: 'Food', value: 6 },
        { name: 'Apparel', value: 4 },
      ],
    },
    {
      name: 'Energy',
      value: 15,
      children: [
        { name: 'Oil & Gas', value: 8 },
        { name: 'Renewable', value: 5 },
        { name: 'Utilities', value: 2 },
      ],
    },
  ];

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        return `${params.name}: ${params.value}`;
      },
    },
    series: [
      {
        type: 'treemap',
        data,
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        label: {
          show: true,
          formatter: '{b}',
          color: '#fff',
          fontSize: 12,
        },
        upperLabel: {
          show: true,
          height: 20,
          color: '#fff',
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
          gapWidth: 2,
        },
        levels: [
          {
            itemStyle: {
              borderWidth: 3,
              gapWidth: 3,
            },
            upperLabel: { show: false },
          },
          {
            colorSaturation: [0.3, 0.6],
            itemStyle: {
              borderColorSaturation: 0.7,
            },
          },
        ],
        color: ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444'],
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default TreemapChart;
