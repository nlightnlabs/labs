import React from 'react';
import { Icon, IconProps } from './Icon';

export const ViewIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </Icon>
);

export default ViewIcon;
