/**
 * Hook for accessing and managing tenant configuration.
 */

import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  initializeTenant,
  fetchCurrentTenant,
  selectTenantConfig,
  selectTenantName,
  selectIsTenantInitialized,
  selectTenantLoading,
  selectTenantError,
} from '@/store/slices/tenantSlice';
import type { TenantConfig } from '@/types';

interface UseTenantConfigReturn {
  /** Current tenant configuration */
  config: TenantConfig | null;
  /** Current tenant name */
  tenantName: string | null;
  /** Whether tenant has been initialized */
  isInitialized: boolean;
  /** Whether tenant is loading */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Initialize tenant based on current origin */
  initialize: () => Promise<TenantConfig | null>;
  /** Refresh tenant configuration */
  refresh: () => Promise<TenantConfig | null>;
}

/**
 * Hook for accessing and managing tenant configuration.
 *
 * @example
 * ```tsx
 * const { config, tenantName, isInitialized, initialize } = useTenantConfig();
 *
 * useEffect(() => {
 *   if (!isInitialized) {
 *     initialize();
 *   }
 * }, [isInitialized, initialize]);
 * ```
 */
export function useTenantConfig(): UseTenantConfigReturn {
  const dispatch = useAppDispatch();

  const config = useAppSelector(selectTenantConfig);
  const tenantName = useAppSelector(selectTenantName);
  const isInitialized = useAppSelector(selectIsTenantInitialized);
  const isLoading = useAppSelector(selectTenantLoading);
  const error = useAppSelector(selectTenantError);

  const initialize = useCallback(async (): Promise<TenantConfig | null> => {
    try {
      const result = await dispatch(initializeTenant()).unwrap();
      console.log('[Tenant] Initialized:', result.tenant_name);
      return result;
    } catch (err) {
      console.error('[Tenant] Initialization failed:', err);
      return null;
    }
  }, [dispatch]);

  const refresh = useCallback(async (): Promise<TenantConfig | null> => {
    try {
      const result = await dispatch(fetchCurrentTenant()).unwrap();
      console.log('[Tenant] Refreshed:', result.tenant_name);
      return result;
    } catch (err) {
      console.error('[Tenant] Refresh failed:', err);
      return null;
    }
  }, [dispatch]);

  return {
    config,
    tenantName,
    isInitialized,
    isLoading,
    error,
    initialize,
    refresh,
  };
}

export default useTenantConfig;
