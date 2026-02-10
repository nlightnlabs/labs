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
  TenantConfig,
} from '@/types';

// Create axios instance - routes are now at root level (not /api/v1)
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
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

// Auth API - Updated to match new main.py routes
export const authApi = {
  // Login using /db/authenticate_user endpoint
  login: (credentials: LoginCredentials) =>
    api.post('/db/authenticate_user', {
      user_record: {
        username: credentials.username || credentials.email,
        password: credentials.password,
      },
      scope: 'tenant',
    }),

  // Register using /db/create_user endpoint
  register: (data: RegisterData) =>
    api.post('/db/create_user', {
      user_record: {
        username: data.email,
        email: data.email,
        first_name: data.firstName,
        last_name: data.lastName,
        company_name: data.companyName,
        password: data.password,
      },
      scope: 'tenant',
    }),

  logout: () => {
    // Clear local storage/session - no backend call needed for simple logout
    return Promise.resolve({ data: { success: true } });
  },

  refresh: (refreshToken: string) =>
    api.post<ApiResponse<{ token: string; refreshToken: string }>>('/auth/refresh', { refreshToken }),

  forgotPassword: (data: PasswordResetRequest) =>
    api.post('/db/reset_password', {
      user_record: {
        username: data.email,
      },
      scope: 'tenant',
    }),

  resetPassword: (data: PasswordResetConfirm) =>
    api.post('/db/reset_password', {
      user_record: {
        username: data.token, // token contains username/email for password reset
        password: data.password,
      },
      scope: 'tenant',
    }),

  verifyEmail: (token: string) =>
    api.post<ApiResponse<{ message: string }>>('/auth/verify-email', { token }),

  // Get current user - uses db/query to fetch user data
  getCurrentUser: () => api.get<ApiResponse<User>>('/users/me'),

  // Update user profile using /db/edit_user
  updateProfile: (data: Partial<User>) =>
    api.post('/db/edit_user', {
      user_record: {
        username: data.email || data.username,
        ...data,
      },
      scope: 'tenant',
    }),

  changePassword: (data: ChangePasswordData & { username: string }) =>
    api.post('/db/reset_password', {
      user_record: {
        username: data.username,
        password: data.newPassword,
      },
      scope: 'tenant',
    }),

  uploadAvatar: (file: FormData) =>
    api.post('/s3/upload_files', file, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  deleteAvatar: () =>
    api.post('/s3/delete_files', { keys: [] }),

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

// Tables CRUD API - Updated to match new main.py routes
export const tablesApi = {
  // List all tables in a schema - uses raw query
  listTables: (dbSchema = 'data', dbName?: string) =>
    api.post('/db/query', {
      query: `SELECT table_name FROM information_schema.tables WHERE table_schema = '${dbSchema}' ORDER BY table_name`,
      db_name: dbName,
      scope: 'tenant',
    }),

  // Get data from a specific table
  getTableData: (tableName: string, dbSchema = 'data', dbName?: string) =>
    api.post<TableDataResponse>('/db/table', {
      table_name: tableName,
      db_schema: dbSchema,
      db_name: dbName,
      scope: 'tenant',
    }),

  // Get table schema (column definitions) - uses raw query
  getTableSchema: (tableName: string, dbSchema = 'data', dbName?: string) =>
    api.post<TableSchemaResponse>('/db/query', {
      query: `
        SELECT
          column_name,
          data_type,
          is_nullable,
          column_default,
          character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = '${dbSchema}'
        AND table_name = '${tableName}'
        ORDER BY ordinal_position
      `,
      db_name: dbName,
      scope: 'tenant',
    }),

  // Create new records
  createRecords: (
    tableName: string,
    records: Record<string, unknown>[],
    dbSchema = 'data',
    dbName?: string,
    dataModel?: Record<string, unknown>
  ) =>
    api.post('/db/insert', {
      table_name: tableName,
      records,
      db_schema: dbSchema,
      db_name: dbName,
      data_model: dataModel,
      scope: 'tenant',
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
    api.post('/db/update', {
      table_name: tableName,
      records,
      db_schema: dbSchema,
      db_name: dbName,
      where_clause: whereClause,
      data_model: dataModel,
      scope: 'tenant',
    }),

  // Delete records
  deleteRecords: (
    tableName: string,
    records?: Record<string, unknown>[],
    dbSchema = 'data',
    dbName?: string,
    whereClause?: Record<string, unknown>[]
  ) =>
    api.delete('/db/delete', {
      data: {
        table_name: tableName,
        records,
        db_schema: dbSchema,
        db_name: dbName,
        where_clause: whereClause,
        scope: 'tenant',
      },
    }),

  // Get unique values from a field
  getUniqueValues: (tableName: string, fieldName: string, dbSchema = 'data', dbName?: string) =>
    api.post('/db/list', {
      table_name: tableName,
      field_name: fieldName,
      db_schema: dbSchema,
      db_name: dbName,
      scope: 'tenant',
    }),

  // Execute raw SQL query
  executeQuery: (query: string, dbName?: string) =>
    api.post('/db/query', {
      query,
      db_name: dbName,
      scope: 'tenant',
    }),
};

// Chat API Types
export interface ChatSession {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface SendMessageResponse {
  id: string;
  user_message_id: string;
  content: string;
  timestamp: string;
  topic?: string;
  is_first_message?: boolean;
}

// Chat API
export const chatApi = {
  // Get all chat sessions for the current user
  getSessions: () =>
    api.get<ApiResponse<ChatSession[]>>('/chats/sessions'),

  // Create a new chat session
  createSession: (data: { title?: string }) =>
    api.post<ApiResponse<ChatSession>>('/chats/sessions', data),

  // Get a specific chat session
  getSession: (sessionId: string) =>
    api.get<ApiResponse<ChatSession>>(`/chats/sessions/${sessionId}`),

  // Update a chat session (e.g., rename)
  updateSession: (sessionId: string, data: { title?: string }) =>
    api.put<ApiResponse<ChatSession>>(`/chats/sessions/${sessionId}`, data),

  // Delete a chat session
  deleteSession: (sessionId: string) =>
    api.delete(`/chats/sessions/${sessionId}`),

  // Get messages for a chat session
  getMessages: (sessionId: string) =>
    api.get<ApiResponse<ChatMessage[]>>(`/chats/sessions/${sessionId}/messages`),

  // Send a message and get AI response
  sendMessage: (sessionId: string, content: string) =>
    api.post<ApiResponse<SendMessageResponse>>(`/chats/sessions/${sessionId}/messages`, {
      content,
    }),
};

// Tenant API - Updated to match new main.py routes
export const tenantApi = {
  /**
   * Initialize tenant configuration based on current origin.
   * Should be called when the app loads.
   */
  initConfig: () =>
    api.post<TenantConfig>('/tenant_config'),

  /**
   * Get current tenant configuration (same endpoint).
   */
  getCurrentConfig: () =>
    api.post<TenantConfig>('/tenant_config'),
};

// S3 File Storage API
export interface S3File {
  file_name: string;
  size_bytes: number;
  key: string;
  file_type: string;
}

export interface S3FetchedFile extends S3File {
  metadata: Record<string, string>;
  content: string;
}

export interface S3UploadedFile {
  file_name: string;
  s3_key: string;
  file_path: string;
  content_type: string;
  size_bytes: number;
}

export interface S3FailedFile {
  file_name: string;
  s3_key?: string;
  error: string;
}

export interface S3UploadFromBrowserResponse {
  status: 'success' | 'partial' | 'error';
  uploaded: S3UploadedFile[];
  failed: S3FailedFile[];
  total: number;
  success_count: number;
  message: string;
}

export const s3Api = {
  // Upload one or more files from browser to S3
  // files: Single File or array of File objects from input[type="file"]
  // relativePaths: Single path or array of paths where files will be saved (extension auto-appended)
  uploadFromBrowser: (files: File | File[], relativePaths: string | string[]) => {
    const formData = new FormData();

    // Normalize to arrays
    const fileArray = Array.isArray(files) ? files : [files];
    const pathArray = Array.isArray(relativePaths) ? relativePaths : [relativePaths];

    // Append each file and path
    fileArray.forEach((file) => {
      formData.append('files', file);
    });
    pathArray.forEach((path) => {
      formData.append('relative_paths', path);
    });

    return api.post<S3UploadFromBrowserResponse>('/s3/upload_from_browser', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // List folders in S3
  listFolders: (prefix?: string) =>
    api.post<string[]>('/s3/list_folders', {
      prefix,
      scope: 'tenant',
    }),

  // List files in S3
  listFiles: (prefix?: string) =>
    api.post<S3File[]>('/s3/list_files', {
      prefix,
      scope: 'tenant',
    }),

  // Fetch file contents from S3
  // If bucket_name is provided, use it directly; otherwise use scope: 'tenant'
  fetchFiles: (keys: string[], bucket_name?: string) =>
    api.post<S3FetchedFile[]>('/s3/fetch_files', {
      keys,
      ...(bucket_name ? { bucket_name } : { scope: 'tenant' }),
    }),

  // Download files from S3
  downloadFiles: (keys: string[], downloadDirectory?: string) =>
    api.post('/s3/download_files', {
      keys,
      download_directory: downloadDirectory,
      scope: 'tenant',
    }),

  // Upload files to S3
  uploadFiles: (prefix: string, localPaths: string[]) =>
    api.post('/s3/upload_files', {
      prefix,
      upload_file_local_paths: localPaths,
      scope: 'tenant',
    }),

  // Save JSON data to S3
  saveJsonData: (key: string, data: unknown[]) =>
    api.post('/s3/save_json_data_file', {
      keys: [key],
      data,
      scope: 'tenant',
    }),

  // Delete files from S3
  deleteFiles: (keys: string[]) =>
    api.post('/s3/delete_files', {
      keys,
      scope: 'tenant',
    }),

  // Save data to S3 (generic)
  saveData: (prefix: string, fileName: string, data: unknown) =>
    api.post('/s3/save_data_in_s3', {
      prefix,
      file_name: fileName,
      data,
      scope: 'tenant',
    }),

};

// Claude AI API
export interface ClaudeAskRequest {
  prompt: string;
  context?: string;
  data?: unknown;
}

export interface ClaudeClassifyRequest {
  data: unknown[];
  categories: string[];
  field?: string;
}

export interface FieldMappingRequest {
  source_fields: string[];
  target_fields: string[];
  context?: string;
}

export const claudeApi = {
  // General question/answer with Claude
  ask: (request: ClaudeAskRequest) =>
    api.post<{ response: string }>('/claude_ask', request),

  // Classify data using Claude
  classify: (request: ClaudeClassifyRequest) =>
    api.post<{ classified_data: unknown[] }>('/claude_classify', request),

  // Map fields using Claude
  mapFields: (request: FieldMappingRequest) =>
    api.post('/map_fields', request),
};

// Email API
export interface EmailRequest {
  to_email: string[];
  subject: string;
  body: string;
  from_email?: string;
  attachments?: unknown[];
}

export const emailApi = {
  // Send email
  send: (request: EmailRequest) =>
    api.post<{ status: string; id: string; detail: string }>('/send_email', request),
};

// Two-Factor Authentication API
export type TwoFactorMethod = 'sms' | 'email' | 'authenticator' | 'backup_codes';

export interface TwoFASetupRequest {
  user_id: string;
  method: TwoFactorMethod;
  contact_info?: string;
}

export interface TwoFASetupResponse {
  success: boolean;
  method: string;
  user_id: string;
  message: string;
  requires_verification?: boolean;
  secret?: string;
  qr_code_url?: string;
  backup_codes?: string[];
}

export interface TwoFAVerifyRequest {
  user_id: string;
  method: TwoFactorMethod;
  verification_code: string;
}

export interface TwoFAStatusResponse {
  user_id: string;
  enabled: boolean;
  method: TwoFactorMethod | null;
  setup_date: string | null;
}

export const twoFactorApi = {
  // Setup 2FA for a user
  setup: (request: TwoFASetupRequest) =>
    api.post<TwoFASetupResponse>('/2fa/setup', request),

  // Verify 2FA setup with a code
  verify: (request: TwoFAVerifyRequest) =>
    api.post<{ success: boolean; enabled: boolean; message: string }>('/2fa/verify', request),

  // Disable 2FA for a user
  disable: (userId: string, verificationCode?: string) =>
    api.post<{ success: boolean; enabled: boolean; message: string }>('/2fa/disable', {
      user_id: userId,
      verification_code: verificationCode,
    }),

  // Get 2FA status for a user
  getStatus: (userId: string) =>
    api.get<TwoFAStatusResponse>(`/2fa/status/${userId}`),

  // Validate a 2FA code during login
  validate: (userId: string, code: string) =>
    api.post<{ success: boolean; message: string }>('/2fa/validate', {
      user_id: userId,
      code,
    }),
};

export default api;
