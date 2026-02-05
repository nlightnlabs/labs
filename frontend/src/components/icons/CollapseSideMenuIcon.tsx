import React from 'react';
import { Icon, IconProps } from './Icon';

export const CollapseSideMenuIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <line x1="9" y1="3" x2="9" y2="21" />
    <polyline points="17 9 14 12 17 15" />
  </Icon>
);

export default CollapseSideMenuIcon;
