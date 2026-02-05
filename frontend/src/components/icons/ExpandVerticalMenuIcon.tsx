import React from 'react';
import { Icon, IconProps } from './Icon';

export const ExpandVerticalMenuIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <polyline points="6 9 12 15 18 9" />
  </Icon>
);

export default ExpandVerticalMenuIcon;
