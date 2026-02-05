import React from 'react';
import { Icon, IconProps } from './Icon';

export const ChartIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </Icon>
);

export default ChartIcon;
