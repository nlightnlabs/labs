import React, { useMemo } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Tooltip } from '../common';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { toggleCollapse, closeMobileNav } from '@/store/slices/navigationSlice';
import { NavItem } from '@/types';
import { sideBarItems } from '@/config';

// Transform config items to NavItem format and group by section
const transformAndGroupItems = (): Map<string, NavItem[]> => {
  const grouped = new Map<string, NavItem[]>();

  sideBarItems.forEach((item) => {
    const navItem: NavItem = {
      id: item.id,
      label: item.label,
      icon: item.name, // Use 'name' to map to icon keys
      path: item.path,
    };

    const section = item.section;
    if (!grouped.has(section)) {
      grouped.set(section, []);
    }
    grouped.get(section)!.push(navItem);
  });

  return grouped;
};

// Icon Components
const icons: Record<string, React.FC<{ className?: string }>> = {
  app1: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  app2: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
    </svg>
  ),
  app3: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
    </svg>
  ),
  chat: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
    </svg>
  ),
  data: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
    </svg>
  ),
  chevronLeft: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
    </svg>
  ),
  chevronRight: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  ),
};

interface NavItemComponentProps {
  item: NavItem;
  isCollapsed: boolean;
  onClick?: () => void;
}

const NavItemComponent: React.FC<NavItemComponentProps> = ({ item, isCollapsed, onClick }) => {
  const { t } = useTranslation();
  const location = useLocation();
  const isActive = location.pathname === item.path || location.pathname.startsWith(`${item.path}/`);
  const Icon = icons[item.icon] || icons.data;

  const linkContent = (
    <NavLink
      to={item.path}
      onClick={onClick}
      className={`nav-item ${isActive ? 'nav-item-active' : ''} ${isCollapsed ? 'justify-center px-2' : ''}`}
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      {!isCollapsed && <span>{t(item.label)}</span>}
      {!isCollapsed && item.badge !== undefined && item.badge > 0 && (
        <span className="ml-auto bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 text-xs font-medium px-2 py-0.5 rounded-full">
          {item.badge > 99 ? '99+' : item.badge}
        </span>
      )}
    </NavLink>
  );

  if (isCollapsed) {
    return (
      <Tooltip content={t(item.label)} position="right">
        {linkContent}
      </Tooltip>
    );
  }

  return linkContent;
};

export const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { isCollapsed, isMobileOpen } = useAppSelector((state) => state.navigation);
  const { user } = useAppSelector((state) => state.auth);

  const handleToggleCollapse = () => {
    dispatch(toggleCollapse());
  };

  const handleCloseMobile = () => {
    dispatch(closeMobileNav());
  };

  // Get grouped sections and filter by user role
  const groupedSections = useMemo(() => {
    const grouped = transformAndGroupItems();
    const filtered = new Map<string, NavItem[]>();

    grouped.forEach((items, section) => {
      const filteredItems = items.filter((item: NavItem) => {
        if (!item.roles) return true;
        return user?.role && item.roles.includes(user.role);
      });
      if (filteredItems.length > 0) {
        filtered.set(section, filteredItems);
      }
    });

    return filtered;
  }, [user?.role]);

  const sectionEntries = Array.from(groupedSections.entries());
  const sidebarWidth = isCollapsed ? 'w-16' : 'w-60';

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={handleCloseMobile}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-16 left-0 bottom-0 ${sidebarWidth} border-r flex flex-col transition-all duration-300 z-40
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        style={{
          backgroundColor: 'var(--bg-card)',
          borderColor: 'var(--border-default)',
        }}
      >
        {/* Collapse Toggle (Desktop only) */}
        <div className="hidden lg:block p-3 border-b" style={{ borderColor: 'var(--border-default)' }}>
          <button
            onClick={handleToggleCollapse}
            className={`nav-item w-full ${isCollapsed ? 'justify-center px-2' : 'justify-end pr-2'}`}
            aria-label={isCollapsed ? t('nav.expand') : t('nav.collapse')}
          >
            {isCollapsed ? (
              <icons.chevronRight className="w-5 h-5" />
            ) : (
              <>
                <icons.chevronLeft className="w-5 h-5" />
                {/* <span>{t('nav.collapse')}</span> */}
              </>
            )}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-3 overflow-y-auto flex flex-col">
          {sectionEntries.map(([sectionName, items], index) => (
            <React.Fragment key={sectionName}>
              {/* Section separator (except for first section) */}
              {index > 0 && (
                <hr className="my-3" style={{ borderColor: 'var(--border-default)' }} />
              )}
              {/* Section items */}
              <div className={`space-y-1 ${index === sectionEntries.length - 1 ? 'flex-1' : ''}`}>
                {items.map((item) => (
                  <NavItemComponent
                    key={item.id}
                    item={item}
                    isCollapsed={isCollapsed}
                    onClick={handleCloseMobile}
                  />
                ))}
              </div>
            </React.Fragment>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
