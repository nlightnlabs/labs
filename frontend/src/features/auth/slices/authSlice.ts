import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { AuthState, User, LoginCredentials, RegisterData } from '@/types';
import { authApi } from '@/services/api';

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Helper function to map database user record to User interface
const mapDatabaseUserToUser = (dbUser: Record<string, unknown>): User => {
  // Determine role from access_level
  let role: 'admin' | 'manager' | 'user' = 'user';
  if (dbUser.access_level === 'Super Admin') {
    role = 'admin';
  } else if (dbUser.access_level === 'Power User') {
    role = 'manager';
  }

  return {
    // Database fields (snake_case)
    id: String(dbUser.id || ''),
    contact_id: dbUser.contact_id as string | null,
    first_name: String(dbUser.first_name || ''),
    last_name: String(dbUser.last_name || ''),
    username: String(dbUser.username || dbUser.email || ''),
    email: String(dbUser.email || ''),
    mobile_phone: String(dbUser.mobile_phone || ''),
    job_title: String(dbUser.job_title || ''),
    company_name: String(dbUser.company_name || ''),
    tenant_name: String(dbUser.tenant_name || ''),
    access_level: String(dbUser.access_level || 'Individual'),
    business_unit: String(dbUser.business_unit || ''),
    avatar_url: dbUser.avatar_url as string | undefined,
    user_type: String(dbUser.user_type || 'Guest'),
    status: String(dbUser.status || 'Active'),
    stage: String(dbUser.stage || 'Enabled'),
    creation_date: dbUser.creation_date as string | undefined,
    last_updated: dbUser.last_updated as string | undefined,
    notes: dbUser.notes as string | null,
    attachments: dbUser.attachments,
    additional_data: dbUser.additional_data,
    // Computed fields
    role,
    isActive: dbUser.status === 'Active',
    isVerified: dbUser.stage === 'Enabled',
    // Legacy camelCase aliases for backwards compatibility
    firstName: String(dbUser.first_name || ''),
    lastName: String(dbUser.last_name || ''),
    avatarUrl: dbUser.avatar_url as string | undefined,
    mobilePhone: String(dbUser.mobile_phone || ''),
    jobTitle: String(dbUser.job_title || ''),
    companyName: String(dbUser.company_name || ''),
    tenantName: String(dbUser.tenant_name || ''),
    accessLevel: String(dbUser.access_level || 'Individual'),
    businessUnit: String(dbUser.business_unit || ''),
    userType: String(dbUser.user_type || 'Guest'),
    createdAt: dbUser.creation_date as string | undefined,
    updatedAt: dbUser.last_updated as string | undefined,
  };
};

// Async thunks - Updated to handle new backend response format
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      const userData = response.data;

      // Backend returns user data directly or with status
      if (userData.status === 'error' || userData.error) {
        return rejectWithValue(userData.message || userData.error || 'Login failed');
      }

      // Backend may return user directly or in a data wrapper
      const dbUser = userData.user || userData.data?.user || userData;

      // Map database record to User interface
      const user = mapDatabaseUserToUser(dbUser);

      return {
        data: {
          user,
          token: userData.token || 'local-session',
          refreshToken: userData.refreshToken || 'local-refresh',
        },
      };
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string; detail?: string } } };
      return rejectWithValue(
        err.response?.data?.detail || err.response?.data?.message || 'Login failed'
      );
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (data: RegisterData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(data);
      const userData = response.data;

      // Backend returns user data directly or with status
      if (userData.status === 'error' || userData.error) {
        return rejectWithValue(userData.message || userData.error || 'Registration failed');
      }

      // Backend may return user directly or in a data wrapper
      const dbUser = userData.user || userData.data?.user || userData;

      // Map database record to User interface
      const user = mapDatabaseUserToUser(dbUser);

      return {
        data: {
          user,
          token: userData.token || 'local-session',
          refreshToken: userData.refreshToken || 'local-refresh',
        },
      };
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string; detail?: string } } };
      return rejectWithValue(
        err.response?.data?.detail || err.response?.data?.message || 'Registration failed'
      );
    }
  }
);

export const refreshTokenThunk = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.refreshToken;
      if (!refreshToken) {
        throw new Error('No refresh token');
      }
      const response = await authApi.refresh(refreshToken);
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      return rejectWithValue(err.response?.data?.message || 'Token refresh failed');
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getCurrentUser();
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      return rejectWithValue(err.response?.data?.message || 'Failed to fetch user');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (data: Partial<User>, { rejectWithValue }) => {
    try {
      const response = await authApi.updateProfile(data);
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      return rejectWithValue(err.response?.data?.message || 'Failed to update profile');
    }
  }
);

export const uploadAvatar = createAsyncThunk(
  'auth/uploadAvatar',
  async (file: File, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await authApi.uploadAvatar(formData);
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      return rejectWithValue(err.response?.data?.message || 'Failed to upload avatar');
    }
  }
);

export const deleteAvatar = createAsyncThunk(
  'auth/deleteAvatar',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.deleteAvatar();
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      return rejectWithValue(err.response?.data?.message || 'Failed to remove avatar');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string; refreshToken: string }>
    ) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
    },
    updateUserField: (
      state,
      action: PayloadAction<Partial<User>>
    ) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data.user;
        state.token = action.payload.data.token;
        state.refreshToken = action.payload.data.refreshToken;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data.user;
        state.token = action.payload.data.token;
        state.refreshToken = action.payload.data.refreshToken;
        state.isAuthenticated = true;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Refresh token
      .addCase(refreshTokenThunk.fulfilled, (state, action) => {
        state.token = action.payload.data.token;
        state.refreshToken = action.payload.data.refreshToken;
      })
      .addCase(refreshTokenThunk.rejected, (state) => {
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data;
        state.isAuthenticated = true;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.isLoading = false;
        state.user = null;
        state.isAuthenticated = false;
      })
      // Update profile
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.user = action.payload.data;
      })
      // Upload avatar
      .addCase(uploadAvatar.fulfilled, (state, action) => {
        if (state.user) {
          const newAvatarUrl = action.payload.data?.avatar_url || action.payload.data?.avatarUrl;
          state.user.avatar_url = newAvatarUrl;
          state.user.avatarUrl = newAvatarUrl; // Keep legacy field in sync
        }
      })
      // Delete avatar
      .addCase(deleteAvatar.fulfilled, (state) => {
        if (state.user) {
          state.user.avatar_url = undefined;
          state.user.avatarUrl = undefined;
        }
      });
  },
});

export const { logout, clearError, setCredentials, updateUserField } = authSlice.actions;

export default authSlice.reducer;
