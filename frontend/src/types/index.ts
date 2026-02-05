// User Types
export type UserRole = 'admin' | 'manager' | 'user';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
  phone?: string;
  role: UserRole;
  isActive: boolean;
  isVerified: boolean;
  emailVerifiedAt?: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
}

export interface UserPreferences {
  id: string;
  userId: string;
  theme: ThemeMode;
  language: string;
  timezone: string;
  notificationSettings: NotificationSettings;
  navCollapsed: boolean;
}

export interface NotificationSettings {
  email: boolean;
  inApp: boolean;
  marketing: boolean;
  security: boolean;
}

// Organization Types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  settings: OrganizationSettings;
  createdAt: string;
  updatedAt: string;
}

export interface OrganizationSettings {
  logo?: string;
  primaryColor?: string;
  defaultRole: UserRole;
  ssoEnabled: boolean;
  mfaRequired: boolean;
}

// Authentication Types
export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  acceptTerms: boolean;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
}

export interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
}

// Session Types
export interface Session {
  id: string;
  userId: string;
  ipAddress: string;
  userAgent: string;
  expiresAt: string;
  createdAt: string;
  isCurrent: boolean;
}

// Notification Types
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  userId: string;
  title: string;
  message: string;
  type: NotificationType;
  isRead: boolean;
  link?: string;
  createdAt: string;
  readAt?: string;
}

// Theme Types
export type ThemeMode = 'light' | 'dark' | 'system' | 'ocean' | 'forest' | 'blossom' | 'sunset';

export interface ThemeState {
  mode: ThemeMode;
  customColors?: CustomThemeColors;
}

export interface ThemeOption {
  id: ThemeMode;
  name: string;
  icon: 'sun' | 'moon' | 'monitor' | 'palette';
  color?: string;
}

export interface CustomThemeColors {
  primary?: string;
  secondary?: string;
  background?: string;
}

// Navigation Types
export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
  children?: NavItem[];
  roles?: UserRole[];
}

export interface NavigationState {
  isCollapsed: boolean;
  isMobileOpen: boolean;
  activeItem: string | null;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: string | null;
  meta?: ApiMeta;
}

export interface ApiMeta {
  page?: number;
  perPage?: number;
  total?: number;
  totalPages?: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  error: string | null;
  meta: {
    page: number;
    perPage: number;
    total: number;
    totalPages: number;
  };
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: ValidationError[];
}

// SAML Provider Types
export interface SAMLProvider {
  id: string;
  organizationId: string;
  providerName: string;
  entityId: string;
  ssoUrl: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Dashboard Types
export interface DashboardStats {
  totalUsers?: number;
  activeUsers?: number;
  totalSessions?: number;
  storageUsed?: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

// Settings Types
export interface APIKey {
  id: string;
  name: string;
  prefix: string;
  createdAt: string;
  lastUsedAt?: string;
  expiresAt?: string;
}

// i18n Types
export type SupportedLanguage = 'en-US' | 'es-ES' | 'fr-FR' | 'de-DE' | 'ja-JP';

export interface LanguageOption {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
}

// Form Types
export interface FormFieldState {
  value: string;
  error: string | null;
  touched: boolean;
}

export type FormState<T extends string> = Record<T, FormFieldState>;
