import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { TenantConfig, TenantState } from '@/types';
import { tenantApi } from '@/services/api';

const initialState: TenantState = {
  config: null,
  isLoading: false,
  isInitialized: false,
  error: null,
};

/**
 * Initialize tenant configuration based on current origin.
 * This should be called when the app first loads.
 */
export const initializeTenant = createAsyncThunk<TenantConfig, void>(
  'tenant/initialize',
  async (_, { rejectWithValue }) => {
    try {
      const response = await tenantApi.initConfig();
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.detail || err.message || 'Failed to initialize tenant');
    }
  }
);

/**
 * Fetch current tenant configuration.
 */
export const fetchCurrentTenant = createAsyncThunk<TenantConfig, void>(
  'tenant/fetchCurrent',
  async (_, { rejectWithValue }) => {
    try {
      const response = await tenantApi.getCurrentConfig();
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.detail || err.message || 'Failed to fetch tenant config');
    }
  }
);

const tenantSlice = createSlice({
  name: 'tenant',
  initialState,
  reducers: {
    setTenantConfig: (state, action: PayloadAction<TenantConfig>) => {
      state.config = action.payload;
      state.isInitialized = action.payload.initialized;
      state.error = null;
    },
    clearTenantConfig: (state) => {
      state.config = null;
      state.isInitialized = false;
      state.error = null;
    },
    setTenantError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Initialize tenant
    builder
      .addCase(initializeTenant.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(initializeTenant.fulfilled, (state, action) => {
        state.isLoading = false;
        state.config = action.payload;
        state.isInitialized = action.payload.initialized;
        state.error = null;
      })
      .addCase(initializeTenant.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch current tenant
    builder
      .addCase(fetchCurrentTenant.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCurrentTenant.fulfilled, (state, action) => {
        state.isLoading = false;
        state.config = action.payload;
        state.isInitialized = action.payload.initialized;
        state.error = null;
      })
      .addCase(fetchCurrentTenant.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setTenantConfig, clearTenantConfig, setTenantError } = tenantSlice.actions;

// Selectors - use optional chaining to handle redux-persist partial state
export const selectTenantConfig = (state: { tenant?: TenantState }) => state.tenant?.config ?? null;
export const selectTenantName = (state: { tenant?: TenantState }) => state.tenant?.config?.tenant_name ?? null;
export const selectIsTenantInitialized = (state: { tenant?: TenantState }) => state.tenant?.isInitialized ?? false;
export const selectTenantLoading = (state: { tenant?: TenantState }) => state.tenant?.isLoading ?? false;
export const selectTenantError = (state: { tenant?: TenantState }) => state.tenant?.error ?? null;

export default tenantSlice.reducer;
