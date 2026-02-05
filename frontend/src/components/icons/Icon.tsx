import React from 'react';

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  /** Icon size in pixels or CSS value */
  size?: number | string;
  /** Stroke color - defaults to currentColor for theme inheritance */
  color?: string;
  /** Fill color - defaults to none */
  fill?: string;
  /** Stroke width */
  strokeWidth?: number;
  /** Additional CSS classes for styling states (hover, active, etc.) */
  className?: string;
}

export const defaultIconProps: Partial<IconProps> = {
  size: 24,
  color: 'currentColor',
  fill: 'none',
  strokeWidth: 2,
};

export const Icon: React.FC<IconProps & { children: React.ReactNode }> = ({
  size = defaultIconProps.size,
  color = defaultIconProps.color,
  fill = defaultIconProps.fill,
  strokeWidth = defaultIconProps.strokeWidth,
  className = '',
  children,
  ...props
}) => {
  const sizeValue = typeof size === 'number' ? `${size}px` : size;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={sizeValue}
      height={sizeValue}
      viewBox="0 0 24 24"
      fill={fill}
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`icon transition-colors duration-200 ${className}`}
      {...props}
    >
      {children}
    </svg>
  );
};

export default Icon;
