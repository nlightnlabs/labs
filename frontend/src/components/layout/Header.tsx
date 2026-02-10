import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Avatar, Dropdown, Tooltip } from '../common';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { logout } from '@/features/auth/slices/authSlice';
import { toggleMobileNav } from '@/store/slices/navigationSlice';
import { setThemeMode, themeOptions } from '@/store/slices/themeSlice';
import { useUserAvatar } from '@/hooks';
import { Notification, ThemeMode } from '@/types';

import {appName} from '../../config';

interface HeaderProps {
  onMenuClick?: () => void;
}

// Theme icons
const ThemeIcons: Record<string, React.FC<{ className?: string }>> = {
  sun: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  moon: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  ),
  monitor: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  palette: ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  ),
};

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { mode: currentTheme } = useAppSelector((state) => state.theme);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch avatar from S3 using the stored path
  const { avatarDataUrl } = useUserAvatar({
    userId: user?.id,
    avatarPath: user?.avatar_url || user?.avatarUrl,
  });

  // Mock notifications for demo
  const notifications: Notification[] = [];
  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleMenuClick = () => {
    dispatch(toggleMobileNav());
    onMenuClick?.();
  };

  const handleThemeChange = (theme: ThemeMode) => {
    dispatch(setThemeMode(theme));
    setShowThemeMenu(false);
  };

  // Get current theme option
  const currentThemeOption = themeOptions.find((t) => t.id === currentTheme) || themeOptions[0];
  const CurrentThemeIcon = ThemeIcons[currentThemeOption.icon];

  const userMenuItems = [
    {
      id: 'profile',
      label: t('header.viewProfile'),
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      onClick: () => window.location.href = '/settings/profile',
    },
    {
      id: 'settings',
      label: t('header.settings'),
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      onClick: () => window.location.href = '/settings',
    },
    {
      id: 'help',
      label: t('header.help'),
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      onClick: () => window.open('/docs', '_blank'),
    },
    { id: 'divider', label: '', divider: true },
    {
      id: 'logout',
      label: t('header.signOut'),
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      ),
      onClick: handleLogout,
      danger: true,
    },
  ];

  return (
    <header
      className="fixed top-0 left-0 right-0 h-16 flex items-center justify-between px-4 lg:px-6 border-b z-30"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border-default)',
      }}
    >
      {/* Left Section */}
      <div className="flex items-center gap-4">
        {/* Mobile Menu Toggle */}
        <button
          onClick={handleMenuClick}
          className="nav-item-btn lg:hidden p-2 rounded-lg transition-colors flex items-center justify-center"
          style={{ color: 'var(--nav-item-icon-color)' }}
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: 'var(--color-primary-600, #2563EB)' }}
          >
            <span className="text-white font-bold text-lg">S</span>
          </div>
          <span className="font-semibold text-lg hidden sm:block" style={{ color: 'var(--text-primary)' }}>
            {appName}
          </span>
        </div>
      </div>

      {/* Center Section - Search */}
      <div className="hidden md:flex flex-1 max-w-xl mx-8">
        <div className="relative w-full">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('header.searchPlaceholder')}
            className="input pl-10"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Home Link */}
        <Tooltip content={t('nav.dashboard')} position="bottom">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `nav-item-btn p-2 rounded-lg transition-colors flex items-center justify-center ${isActive ? 'active' : ''}`
            }
            style={({ isActive }) => ({
              backgroundColor: isActive ? 'var(--nav-item-active-bg)' : undefined,
              color: isActive ? 'var(--nav-item-active-color)' : 'var(--nav-item-icon-color)',
            })}
            aria-label={t('nav.dashboard')}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </NavLink>
        </Tooltip>

        {/* Theme Toggle */}
        <div className="relative">
          <Tooltip content="Theme" position="bottom">
            <button
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="nav-item-btn p-2 rounded-lg transition-colors flex items-center justify-center"
              style={{ color: 'var(--nav-item-icon-color)' }}
              aria-label="Toggle theme"
            >
              <CurrentThemeIcon className="w-5 h-5" />
            </button>
          </Tooltip>

          {/* Theme Dropdown */}
          {showThemeMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowThemeMenu(false)}
              />
              <div
                className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg border py-2 z-20"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-default)',
                }}
              >
                <div
                  className="px-3 py-2 text-xs font-semibold uppercase tracking-wide border-b mb-1"
                  style={{ color: 'var(--text-tertiary)', borderColor: 'var(--border-default)' }}
                >
                  Theme
                </div>
                {themeOptions.map((theme) => {
                  const ThemeIcon = ThemeIcons[theme.icon];
                  const isActive = currentTheme === theme.id;
                  return (
                    <button
                      key={theme.id}
                      onClick={() => handleThemeChange(theme.id)}
                      className={`nav-item-btn w-full px-3 py-2 flex items-center gap-3 text-sm transition-colors ${isActive ? 'active' : ''}`}
                      style={{
                        color: 'var(--text-primary)',
                        backgroundColor: isActive ? 'var(--nav-item-active-bg)' : undefined,
                      }}
                    >
                      <span
                        className="flex items-center justify-center w-6 h-6 rounded-full"
                        style={{
                          backgroundColor: theme.color || (theme.id === 'dark' ? '#1F2937' : theme.id === 'light' ? '#F3F4F6' : '#E5E7EB'),
                          color: theme.color ? '#FFFFFF' : (theme.id === 'dark' ? '#F9FAFB' : '#374151'),
                        }}
                      >
                        <ThemeIcon className="w-3.5 h-3.5" />
                      </span>
                      <span className="flex-1 text-left">{theme.name}</span>
                      {isActive && (
                        <svg className="w-4 h-4" style={{ color: 'var(--nav-item-active-color)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Settings Link */}
        <Tooltip content={t('nav.settings')} position="bottom">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `nav-item-btn p-2 rounded-lg transition-colors flex items-center justify-center ${isActive ? 'active' : ''}`
            }
            style={({ isActive }) => ({
              backgroundColor: isActive ? 'var(--nav-item-active-bg)' : undefined,
              color: isActive ? 'var(--nav-item-active-color)' : 'var(--nav-item-icon-color)',
            })}
            aria-label={t('nav.settings')}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </NavLink>
        </Tooltip>

        {/* Divider */}
        <div className="h-6 w-px mx-1" style={{ backgroundColor: 'var(--border-default)' }} />

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="nav-item-btn relative p-2 rounded-lg transition-colors flex items-center justify-center"
            style={{ color: 'var(--nav-item-icon-color)' }}
            aria-label={t('header.notifications')}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div
              className="absolute right-0 mt-2 w-80 rounded-lg shadow-lg border py-2"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-default)',
              }}
            >
              <div className="px-4 py-2 border-b" style={{ borderColor: 'var(--border-default)' }}>
                <h3 className="font-semibold">{t('header.notifications')}</h3>
              </div>
              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center" style={{ color: 'var(--text-tertiary)' }}>
                  {t('header.noNotifications')}
                </div>
              ) : (
                <div className="max-h-96 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className="nav-item-btn px-4 py-3 cursor-pointer"
                      style={{
                        backgroundColor: !notification.isRead ? 'var(--nav-item-active-bg)' : undefined,
                      }}
                    >
                      <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{notification.title}</p>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>{notification.message}</p>
                    </div>
                  ))}
                </div>
              )}
              <div className="px-4 py-2 border-t" style={{ borderColor: 'var(--border-default)' }}>
                <button className="text-sm" style={{ color: 'var(--text-link)' }}>
                  {t('header.viewAllNotifications')}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <Dropdown
          trigger={
            <div className="nav-item-btn flex items-center gap-3 p-1.5 rounded-lg transition-colors cursor-pointer">
              {/* Profile Image - fetched from S3 using avatar_url path */}
              <Avatar
                src={avatarDataUrl || undefined}
                name={user ? `${user.first_name || user.firstName || ''} ${user.last_name || user.lastName || ''}` : undefined}
                size="sm"
              />
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {user ? `${user.first_name || user.firstName || ''} ${user.last_name || user.lastName || ''}` : 'User'}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {user?.job_title || user?.jobTitle || user?.username}
                </p>
              </div>
              <svg className="w-4 h-4 hidden md:block" style={{ color: 'var(--text-tertiary)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          }
          items={userMenuItems}
        />
      </div>
    </header>
  );
};

export default Header;
