import React from 'react';
import { BaseChart } from './BaseChart';
import type { EChartsOption } from 'echarts';

interface CandlestickChartProps {
  title: string;
  height?: number;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  title,
  height = 300,
}) => {
  // Data format: [open, close, low, high]
  const rawData = [
    ['2024-01', 2320.26, 2320.26, 2287.3, 2362.94],
    ['2024-02', 2300, 2291.3, 2288.26, 2308.38],
    ['2024-03', 2295.35, 2346.5, 2295.35, 2346.92],
    ['2024-04', 2347.22, 2358.98, 2337.35, 2363.8],
    ['2024-05', 2360.75, 2382.48, 2347.89, 2383.76],
    ['2024-06', 2383.43, 2385.42, 2371.23, 2391.82],
    ['2024-07', 2377.41, 2419.02, 2369.57, 2421.15],
    ['2024-08', 2425.92, 2428.15, 2417.58, 2440.38],
    ['2024-09', 2411, 2433.13, 2403.3, 2437.42],
    ['2024-10', 2432.68, 2434.48, 2427.7, 2441.73],
    ['2024-11', 2430.69, 2418.53, 2394.22, 2433.89],
    ['2024-12', 2416.62, 2432.4, 2414.4, 2443.03],
  ];

  const dates = rawData.map((item) => item[0]);
  const data = rawData.map((item) => item.slice(1));

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '10%',
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: true,
      axisLabel: { color: '#666' },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: { color: '#666' },
      splitLine: {
        lineStyle: { type: 'dashed', color: '#eee' },
      },
    },
    series: [
      {
        type: 'candlestick',
        data,
        itemStyle: {
          color: '#10B981',
          color0: '#EF4444',
          borderColor: '#10B981',
          borderColor0: '#EF4444',
        },
      },
    ],
  };

  return <BaseChart title={title} option={option} height={height} />;
};

export default CandlestickChart;
