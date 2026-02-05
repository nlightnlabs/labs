import React from 'react';

interface ChartCardProps {
  title: string;
  type?: 'line' | 'bar' | 'pie' | 'area';
  data?: number[];
}

// Simple chart visualizations using CSS
const LineChart: React.FC<{ data: number[] }> = ({ data }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  return (
    <div className="h-40 flex items-end gap-1 p-4">
      <svg className="w-full h-full" viewBox="0 0 100 50" preserveAspectRatio="none">
        <defs>
          <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(59, 130, 246)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="rgb(59, 130, 246)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d={`M 0 ${50 - ((data[0] - min) / range) * 40} ${data
            .map((d, i) => `L ${(i / (data.length - 1)) * 100} ${50 - ((d - min) / range) * 40}`)
            .join(' ')} L 100 50 L 0 50 Z`}
          fill="url(#lineGradient)"
        />
        <path
          d={`M 0 ${50 - ((data[0] - min) / range) * 40} ${data
            .map((d, i) => `L ${(i / (data.length - 1)) * 100} ${50 - ((d - min) / range) * 40}`)
            .join(' ')}`}
          fill="none"
          stroke="rgb(59, 130, 246)"
          strokeWidth="2"
        />
      </svg>
    </div>
  );
};

const BarChart: React.FC<{ data: number[] }> = ({ data }) => {
  const max = Math.max(...data);
  const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4'];

  return (
    <div className="h-40 flex items-end justify-around gap-2 p-4">
      {data.map((value, index) => (
        <div
          key={index}
          className="flex-1 rounded-t transition-all hover:opacity-80"
          style={{
            height: `${(value / max) * 100}%`,
            backgroundColor: colors[index % colors.length],
            minHeight: '8px',
          }}
        />
      ))}
    </div>
  );
};

const PieChart: React.FC<{ data: number[] }> = ({ data }) => {
  const total = data.reduce((sum, d) => sum + d, 0);
  const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444'];
  let currentAngle = 0;

  return (
    <div className="h-40 flex items-center justify-center p-4">
      <svg viewBox="0 0 100 100" className="w-32 h-32">
        {data.map((value, index) => {
          const angle = (value / total) * 360;
          const startAngle = currentAngle;
          const endAngle = currentAngle + angle;
          currentAngle = endAngle;

          const start = polarToCartesian(50, 50, 40, startAngle);
          const end = polarToCartesian(50, 50, 40, endAngle);
          const largeArcFlag = angle > 180 ? 1 : 0;

          const d = [
            `M 50 50`,
            `L ${start.x} ${start.y}`,
            `A 40 40 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
            `Z`,
          ].join(' ');

          return (
            <path
              key={index}
              d={d}
              fill={colors[index % colors.length]}
              className="hover:opacity-80 transition-opacity"
            />
          );
        })}
      </svg>
    </div>
  );
};

const AreaChart: React.FC<{ data: number[] }> = ({ data }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  return (
    <div className="h-40 flex items-end gap-1 p-4">
      <svg className="w-full h-full" viewBox="0 0 100 50" preserveAspectRatio="none">
        <defs>
          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(139, 92, 246)" stopOpacity="0.4" />
            <stop offset="100%" stopColor="rgb(139, 92, 246)" stopOpacity="0.05" />
          </linearGradient>
        </defs>
        <path
          d={`M 0 50 ${data
            .map((d, i) => `L ${(i / (data.length - 1)) * 100} ${50 - ((d - min) / range) * 40}`)
            .join(' ')} L 100 50 Z`}
          fill="url(#areaGradient)"
        />
        <path
          d={`M 0 ${50 - ((data[0] - min) / range) * 40} ${data
            .map((d, i) => `L ${(i / (data.length - 1)) * 100} ${50 - ((d - min) / range) * 40}`)
            .join(' ')}`}
          fill="none"
          stroke="rgb(139, 92, 246)"
          strokeWidth="2"
        />
      </svg>
    </div>
  );
};

function polarToCartesian(cx: number, cy: number, r: number, angle: number) {
  const rad = ((angle - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  type = 'line',
  data = [30, 45, 35, 50, 40, 60, 55, 70, 65, 80, 75, 90],
}) => {
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <BarChart data={data} />;
      case 'pie':
        return <PieChart data={data.slice(0, 5)} />;
      case 'area':
        return <AreaChart data={data} />;
      default:
        return <LineChart data={data} />;
    }
  };

  return (
    <div
      className="rounded-xl overflow-hidden transition-shadow hover:shadow-md"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div className="px-5 py-4 border-b" style={{ borderColor: 'var(--border-default)' }}>
        <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          {title}
        </h3>
      </div>
      {renderChart()}
    </div>
  );
};

export default ChartCard;
