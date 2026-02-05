import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '@/store';
import { logout, refreshTokenThunk } from '@/features/auth/slices/authSlice';
import {
  LoginCredentials,
  RegisterData,
  User,
  UserPreferences,
  PasswordResetRequest,
  PasswordResetConfirm,
  ChangePasswordData,
  Notification,
  Session,
  Organization,
  SAMLProvider,
  ApiResponse,
  PaginatedResponse,
} from '@/types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const state = store.getState();
    const token = state.auth.token;

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await store.dispatch(refreshTokenThunk()).unwrap();
        processQueue(null);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error);
        store.dispatch(logout());
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<ApiResponse<{ user: User; token: string; refreshToken: string }>>('/auth/login', credentials),

  register: (data: RegisterData) =>
    api.post<ApiResponse<{ user: User; token: string; refreshToken: string }>>('/auth/register', data),

  logout: () => api.post('/auth/logout'),

  refresh: (refreshToken: string) =>
    api.post<ApiResponse<{ token: string; refreshToken: string }>>('/auth/refresh', { refreshToken }),

  forgotPassword: (data: PasswordResetRequest) =>
    api.post<ApiResponse<{ message: string }>>('/auth/forgot-password', data),

  resetPassword: (data: PasswordResetConfirm) =>
    api.post<ApiResponse<{ message: string }>>('/auth/reset-password', data),

  verifyEmail: (token: string) =>
    api.post<ApiResponse<{ message: string }>>('/auth/verify-email', { token }),

  getCurrentUser: () => api.get<ApiResponse<User>>('/users/me'),

  updateProfile: (data: Partial<User>) => api.put<ApiResponse<User>>('/users/me', data),

  changePassword: (data: ChangePasswordData) =>
    api.patch<ApiResponse<{ message: string }>>('/users/me/password', data),

  uploadAvatar: (file: FormData) =>
    api.patch<ApiResponse<{ avatarUrl: string }>>('/users/me/avatar', file, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  deleteAvatar: () =>
    api.delete<ApiResponse<{ message: string }>>('/users/me/avatar'),

  deleteAccount: () => api.delete('/users/me'),

  // SAML
  getSAMLMetadata: () => api.get('/auth/saml/metadata'),

  initiateSAMLLogin: (providerId: string) =>
    api.get<ApiResponse<{ redirectUrl: string }>>(`/auth/saml/login/${providerId}`),
};

// Users API
export const usersApi = {
  getSessions: () => api.get<ApiResponse<Session[]>>('/users/me/sessions'),

  revokeSession: (sessionId: string) => api.delete(`/users/me/sessions/${sessionId}`),

  revokeAllSessions: () => api.delete('/users/me/sessions'),
};

// Settings API
export const settingsApi = {
  getPreferences: () => api.get<ApiResponse<UserPreferences>>('/settings/preferences'),

  updatePreferences: (data: Partial<UserPreferences>) =>
    api.put<ApiResponse<UserPreferences>>('/settings/preferences', data),

  getOrganization: () => api.get<ApiResponse<Organization>>('/settings/organization'),

  updateOrganization: (data: Partial<Organization>) =>
    api.put<ApiResponse<Organization>>('/settings/organization', data),

  getSAMLProviders: () => api.get<ApiResponse<SAMLProvider[]>>('/settings/saml-providers'),

  createSAMLProvider: (data: Partial<SAMLProvider>) =>
    api.post<ApiResponse<SAMLProvider>>('/settings/saml-providers', data),

  updateSAMLProvider: (id: string, data: Partial<SAMLProvider>) =>
    api.put<ApiResponse<SAMLProvider>>(`/settings/saml-providers/${id}`, data),

  deleteSAMLProvider: (id: string) => api.delete(`/settings/saml-providers/${id}`),
};

// Notifications API
export const notificationsApi = {
  getAll: (page = 1, perPage = 20) =>
    api.get<PaginatedResponse<Notification>>('/notifications', {
      params: { page, per_page: perPage },
    }),

  markAsRead: (id: string) => api.patch(`/notifications/${id}/read`),

  markAllAsRead: () => api.patch('/notifications/read-all'),

  delete: (id: string) => api.delete(`/notifications/${id}`),
};

// Tables CRUD API
export interface TableInfo {
  name: string;
  displayName?: string;
}

export interface ColumnSchema {
  name: string;
  type: string;
  nullable: boolean;
  default: string | null;
  maxLength: number | null;
}

export interface TableDataResponse {
  success: boolean;
  data: Record<string, unknown>[];
  count: number;
}

export interface TableListResponse {
  tables: string[];
  count: number;
}

export interface TableSchemaResponse {
  success: boolean;
  table: string;
  columns: ColumnSchema[];
}

export const tablesApi = {
  // List all tables in a schema
  listTables: (dbSchema = 'data', dbName?: string) =>
    api.get<TableListResponse>('/tables/list', {
      params: { db_schema: dbSchema, db_name: dbName },
    }),

  // Get data from a specific table
  getTableData: (tableName: string, dbSchema = 'data', dbName?: string) =>
    api.post<TableDataResponse>('/tables/data', {
      table_name: tableName,
      db_schema: dbSchema,
      db_name: dbName,
    }),

  // Get table schema (column definitions)
  getTableSchema: (tableName: string, dbSchema = 'data', dbName?: string) =>
    api.get<TableSchemaResponse>(`/tables/schema/${tableName}`, {
      params: { db_schema: dbSchema, db_name: dbName },
    }),

  // Create new records
  createRecords: (
    tableName: string,
    records: Record<string, unknown>[],
    dbSchema = 'data',
    dbName?: string,
    dataModel?: Record<string, unknown>
  ) =>
    api.post('/tables/records/create', {
      table_name: tableName,
      records,
      db_schema: dbSchema,
      db_name: dbName,
      data_model: dataModel,
    }),

  // Update existing records
  updateRecords: (
    tableName: string,
    records: Record<string, unknown>[],
    dbSchema = 'data',
    dbName?: string,
    whereClause?: Record<string, unknown>[],
    dataModel?: Record<string, unknown>
  ) =>
    api.post('/tables/records/update', {
      table_name: tableName,
      records,
      db_schema: dbSchema,
      db_name: dbName,
      where_clause: whereClause,
      data_model: dataModel,
    }),

  // Delete records
  deleteRecords: (
    tableName: string,
    records?: Record<string, unknown>[],
    dbSchema = 'data',
    dbName?: string,
    whereClause?: Record<string, unknown>[]
  ) =>
    api.post('/tables/records/delete', {
      table_name: tableName,
      records,
      db_schema: dbSchema,
      db_name: dbName,
      where_clause: whereClause,
    }),

  // Get unique values from a field
  getUniqueValues: (tableName: string, fieldName: string, dbSchema = 'data', dbName?: string) =>
    api.post('/tables/unique-values', {
      table_name: tableName,
      field_name: fieldName,
      db_schema: dbSchema,
      db_name: dbName,
    }),

  // Execute raw SQL query
  executeQuery: (query: string, dbName?: string) =>
    api.post('/tables/query', {
      query,
      db_name: dbName,
    }),
};

export default api;
