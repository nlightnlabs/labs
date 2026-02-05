import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useAppSelector } from '@/store/hooks';

interface LayoutProps {
  children?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isCollapsed } = useAppSelector((state) => state.navigation);

  const mainMarginLeft = isCollapsed ? 'lg:ml-16' : 'lg:ml-60';

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-page)' }}>
      <Header />
      <Sidebar />
      <main
        className={`pt-16 ${mainMarginLeft} transition-all duration-300`}
      >
        <div className="p-4 lg:p-6">
          {children || <Outlet />}
        </div>
      </main>
    </div>
  );
};

export default Layout;
