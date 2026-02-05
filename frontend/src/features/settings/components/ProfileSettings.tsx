import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Input, Button, Avatar, Alert } from '@/components/common';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { updateProfile, uploadAvatar, deleteAvatar } from '@/features/auth/slices/authSlice';

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export const ProfileSettings: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { user, isLoading } = useAppSelector((state) => state.auth);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: user?.mobilePhone || '',
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    try {
      await dispatch(updateProfile(formData)).unwrap();
      setMessage({ type: 'success', text: t('settings.profile.updated') });
    } catch {
      setMessage({ type: 'error', text: t('errors.general') });
    }
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setMessage({ type: 'error', text: 'Invalid file type. Allowed: JPEG, PNG, GIF, WebP' });
      return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setMessage({ type: 'error', text: 'File too large. Maximum size is 5MB' });
      return;
    }

    setMessage(null);
    setIsUploading(true);

    try {
      await dispatch(uploadAvatar(file)).unwrap();
      setMessage({ type: 'success', text: 'Avatar updated successfully' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to upload avatar' });
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemoveAvatar = async () => {
    if (!user?.avatarUrl) return;

    setMessage(null);
    setIsUploading(true);

    try {
      await dispatch(deleteAvatar()).unwrap();
      setMessage({ type: 'success', text: 'Avatar removed successfully' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to remove avatar' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader
        title={t('settings.profile.title')}
        subtitle={t('settings.profile.subtitle')}
      />
      <CardBody>
        {message && (
          <Alert
            variant={message.type}
            className="mb-4"
            onClose={() => setMessage(null)}
          >
            {message.text}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Avatar Section */}
          <div className="flex items-center gap-6">
            <Avatar
              src={user?.avatarUrl}
              name={user ? `${user.firstName} ${user.lastName}` : undefined}
              size="xl"
            />
            <div>
              <h4 className="font-medium" style={{ color: 'var(--text-primary)' }}>
                {t('settings.profile.avatar')}
              </h4>
              <div className="flex gap-2 mt-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAvatarClick}
                  isLoading={isUploading}
                  disabled={isUploading}
                >
                  {t('settings.profile.changeAvatar')}
                </Button>
                {user?.avatarUrl && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleRemoveAvatar}
                    disabled={isUploading}
                  >
                    {t('settings.profile.removeAvatar')}
                  </Button>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label={t('settings.profile.firstName')}
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
            />
            <Input
              label={t('settings.profile.lastName')}
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
            />
          </div>

          <Input
            label={t('settings.profile.email')}
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            disabled
            helperText="Email cannot be changed"
          />

          <Input
            label={t('settings.profile.phone')}
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+1 (555) 000-0000"
          />

          <div className="flex justify-end">
            <Button type="submit" isLoading={isLoading}>
              {t('common.save')}
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
};

export default ProfileSettings;
