import { useState, useEffect, useCallback } from 'react';
import { s3Api } from '@/services/api';
import { useTenantConfig } from './useTenantConfig';

const AVATAR_CACHE_KEY = 'cached_avatar';

// Helper to get MIME type from file extension
const getMimeType = (path: string): string => {
  const ext = path.split('.').pop()?.toLowerCase();
  const mimeTypes: Record<string, string> = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    webp: 'image/webp',
  };
  return mimeTypes[ext || ''] || 'image/png';
};

interface UseUserAvatarOptions {
  userId?: string;
  avatarPath?: string | null;
}

interface UseUserAvatarResult {
  avatarDataUrl: string | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  clearCache: () => void;
}

/**
 * Hook to fetch and cache user avatar from S3
 * @param options.userId - The user ID for cache key
 * @param options.avatarPath - The relative S3 path to the avatar (e.g., "images/123-username/avatar.jpg")
 * @returns Avatar data URL, loading state, and utility functions
 */
export const useUserAvatar = ({ userId, avatarPath }: UseUserAvatarOptions): UseUserAvatarResult => {
  const { config: tenantConfig } = useTenantConfig();
  const [avatarDataUrl, setAvatarDataUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cacheKey = `${AVATAR_CACHE_KEY}_${userId}`;

  const clearCache = useCallback(() => {
    if (userId) {
      localStorage.removeItem(cacheKey);
      setAvatarDataUrl(null);
    }
  }, [userId, cacheKey]);

  const fetchAvatar = useCallback(async () => {
    if (!avatarPath || !tenantConfig?.s3_root_prefix || !userId) {
      setAvatarDataUrl(null);
      return;
    }

    // Check localStorage cache first
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { path, dataUrl } = JSON.parse(cached);
        if (path === avatarPath) {
          setAvatarDataUrl(dataUrl);
          return;
        }
      } catch {
        // Invalid cache, continue to fetch
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      // Construct full S3 key: {s3_root_prefix}/{relative_path}
      const rootPrefix = (tenantConfig.s3_root_prefix || '').replace(/\/$/, '');
      const fullS3Key = `${rootPrefix}/${avatarPath}`;
      const bucket = tenantConfig.s3_bucket;

      // Fetch file from S3
      const response = await s3Api.fetchFiles([fullS3Key], bucket);
      const files = response.data;

      if (files && files.length > 0) {
        const file = files[0];
        // Content is base64 encoded for binary files
        const mimeType = getMimeType(avatarPath);
        const dataUrl = `data:${mimeType};base64,${file.content}`;

        // Cache in localStorage
        localStorage.setItem(cacheKey, JSON.stringify({ path: avatarPath, dataUrl }));

        setAvatarDataUrl(dataUrl);
      } else {
        setAvatarDataUrl(null);
      }
    } catch (err) {
      console.error('Failed to fetch avatar from S3:', err);
      setError('Failed to load avatar');
      // Clear cache on error
      localStorage.removeItem(cacheKey);
      setAvatarDataUrl(null);
    } finally {
      setIsLoading(false);
    }
  }, [avatarPath, tenantConfig, userId, cacheKey]);

  // Fetch avatar when path changes
  useEffect(() => {
    fetchAvatar();
  }, [fetchAvatar]);

  return {
    avatarDataUrl,
    isLoading,
    error,
    refetch: fetchAvatar,
    clearCache,
  };
};

export default useUserAvatar;
