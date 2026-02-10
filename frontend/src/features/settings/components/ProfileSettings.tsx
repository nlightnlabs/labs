import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardBody, Input, Button, Avatar, Alert } from '@/components/common';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { updateUserField } from '@/features/auth/slices/authSlice';
import { tablesApi, s3Api } from '@/services/api';
import { useUserAvatar } from '@/hooks';

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export const ProfileSettings: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState({
    firstName: user?.first_name || user?.firstName || '',
    lastName: user?.last_name || user?.lastName || '',
    email: user?.email || '',
    phone: user?.mobile_phone || user?.mobilePhone || '',
    jobTitle: user?.job_title || '',
    avatar_url: user?.avatar_url || user?.avatarUrl || '',
    companyName: user?.company_name || '',
    businessUnit: user?.business_unit || '',
    notes: user?.notes || '',
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [emailValidation, setEmailValidation] = useState<{
    status: 'idle' | 'checking' | 'valid' | 'invalid';
    message?: string;
  }>({ status: 'idle' });
  const originalEmail = useRef(user?.email || '');

  // Track the avatar path - use formData.avatar_url for newly uploaded avatars
  const [pendingAvatarPath, setPendingAvatarPath] = useState<string | null>(null);

  // Use the shared hook to fetch avatar from S3
  // Use pending path if uploading new avatar, otherwise use path from Redux/formData
  const currentAvatarPath = pendingAvatarPath || formData.avatar_url || null;
  const { avatarDataUrl, clearCache, refetch } = useUserAvatar({
    userId: user?.id,
    avatarPath: currentAvatarPath,
  });

  // Fetch user data from backend
  useEffect(() => {
    const fetchUserData = async () => {
      if (!user?.id && !user?.email) return;

      setIsLoadingProfile(true);
      try {
        const response = await tablesApi.getTableData('users', 'data');
        const users = response.data?.data || [];
        const currentUser = users.find(
          (u: Record<string, unknown>) => u.id === user?.id || u.email === user?.email
        );

        if (currentUser) {
          setFormData({
            firstName: (currentUser.first_name as string) || '',
            lastName: (currentUser.last_name as string) || '',
            email: (currentUser.email as string) || '',
            phone: (currentUser.mobile_phone as string) || '',
            jobTitle: (currentUser.job_title as string) || '',
            avatar_url: (currentUser.avatar_url as string) || '',
            companyName: (currentUser.company_name as string) || '',
            businessUnit: (currentUser.business_unit as string) || '',
            notes: (currentUser.notes as string) || '',
          });
          // avatar_url is already set in formData above, which drives the useUserAvatar hook
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setIsLoadingProfile(false);
      }
    };

    fetchUserData();
  }, [user?.id, user?.email]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Reset email validation when email changes
    if (name === 'email') {
      setEmailValidation({ status: 'idle' });
    }
  };

  const handleEmailBlur = async () => {
    const newEmail = formData.email.trim().toLowerCase();
    const origEmail = originalEmail.current.toLowerCase();

    // Skip validation if email hasn't changed or is empty
    if (!newEmail || newEmail === origEmail) {
      setEmailValidation({ status: 'idle' });
      return;
    }

    setEmailValidation({ status: 'checking' });

    try {
      const response = await tablesApi.getTableData('users', 'data');
      const users = response.data?.data || [];
      const emailExists = users.some(
        (u: Record<string, unknown>) =>
          (u.email as string)?.toLowerCase() === newEmail && u.id !== user?.id
      );

      if (emailExists) {
        setEmailValidation({
          status: 'invalid',
          message: 'Email exists. Please provide another.',
        });
      } else {
        setEmailValidation({
          status: 'valid',
          message: 'Email is available',
        });
      }
    } catch (error) {
      console.error('Failed to validate email:', error);
      setEmailValidation({ status: 'idle' });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    // Don't save if email validation failed
    if (emailValidation.status === 'invalid') {
      setMessage({ type: 'error', text: 'Please fix the email address before saving.' });
      return;
    }

    setIsSaving(true);

    try {
      // Update the user record in data.users table
      // Include 'id' in the record to use the backend's ID-based update mode
      const updateRecord = {
        id: user?.id,
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        mobile_phone: formData.phone,
        job_title: formData.jobTitle,
        avatar_url: formData.avatar_url,
        company_name: formData.companyName,
        business_unit: formData.businessUnit,
        notes: formData.notes,
        last_updated: new Date().toISOString(),
      };

      console.log('Saving profile with updateRecord:', updateRecord);
      console.log('user.id:', user?.id, 'type:', typeof user?.id);
      console.log('formData.avatar_url:', formData.avatar_url);

      const updateResult = await tablesApi.updateRecords(
        'users',
        [updateRecord],
        'data'
      );

      console.log('Update result:', updateResult);

      // Update the original email reference
      originalEmail.current = formData.email;
      setEmailValidation({ status: 'idle' });

      // Clear pending avatar path since it's now saved
      setPendingAvatarPath(null);

      // Update Redux state so Header and other components reflect the changes
      dispatch(updateUserField({
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        mobile_phone: formData.phone,
        job_title: formData.jobTitle,
        avatar_url: formData.avatar_url,
        company_name: formData.companyName,
        business_unit: formData.businessUnit,
        notes: formData.notes,
      }));

      setMessage({ type: 'success', text: t('settings.profile.updated') });
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: t('errors.general') });
    } finally {
      setIsSaving(false);
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

    if (!user?.id || !user?.username) {
      setMessage({ type: 'error', text: 'User information not available' });
      return;
    }

    setMessage(null);
    setIsUploading(true);

    try {
      // Construct relative path for S3: images/{user_id}-{username}/avatar
      // Extension will be auto-appended by the backend based on the uploaded file
      const relativePath = `images/${user.id}-${user.username}/avatar`;

      // Upload file to S3 using the new generic upload endpoint
      const uploadResponse = await s3Api.uploadFromBrowser(file, relativePath);

      // Check if upload was successful
      if (uploadResponse.data.status === 'error' || uploadResponse.data.success_count === 0) {
        throw new Error(uploadResponse.data.failed?.[0]?.error || 'Upload failed');
      }

      // Get the relative path returned from S3 (e.g., "images/123-johndoe/avatar.png")
      const newAvatarPath = uploadResponse.data.uploaded[0].file_path;

      // Clear cached avatar to force re-fetch with new path
      clearCache();

      // Set pending avatar path to trigger hook refetch for preview
      setPendingAvatarPath(newAvatarPath);

      // Store the new avatar_url in formData - will be saved to database when Save button is clicked
      console.log('Setting avatar_url in formData to:', newAvatarPath);
      setFormData((prev) => {
        const updated = { ...prev, avatar_url: newAvatarPath };
        console.log('Updated formData:', updated);
        return updated;
      });

      setMessage({ type: 'success', text: 'Avatar uploaded. Click Save to update your profile.' });
    } catch (error) {
      console.error('Failed to upload avatar:', error);
      setMessage({ type: 'error', text: 'Failed to upload avatar' });
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemoveAvatar = () => {
    if (!avatarDataUrl && !formData.avatar_url) return;
    if (!user?.id) return;

    // Clear cached avatar and pending path
    clearCache();
    setPendingAvatarPath(null);

    // Clear avatar_url in formData - will be saved to database when Save button is clicked
    setFormData((prev) => ({ ...prev, avatar_url: '' }));

    setMessage({ type: 'success', text: 'Avatar removed. Click Save to update your profile.' });
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
              src={avatarDataUrl || undefined}
              name={user ? `${formData.firstName || user.first_name || user.firstName || ''} ${formData.lastName || user.last_name || user.lastName || ''}` : undefined}
              size="xl"
            />
            <div>
              <div className="flex gap-2">
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
                {avatarDataUrl && (
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

          <div className="w-full">
            <Input
              label={t('settings.profile.email')}
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              onBlur={handleEmailBlur}
              disabled={isLoadingProfile}
            />
            {emailValidation.status === 'checking' && (
              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                Checking email availability...
              </p>
            )}
            {emailValidation.status === 'invalid' && (
              <p className="text-sm mt-1 flex items-center gap-1" style={{ color: 'var(--color-error-500)' }}>
                <span>✕</span> {emailValidation.message}
              </p>
            )}
            {emailValidation.status === 'valid' && (
              <p className="text-sm mt-1 flex items-center gap-1" style={{ color: 'var(--color-success-500)' }}>
                <span>✓</span> {emailValidation.message}
              </p>
            )}
          </div>

          <Input
            label={t('settings.profile.phone')}
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+1 (555) 000-0000"
          />

          <Input
            label="Job Title"
            name="jobTitle"
            value={formData.jobTitle}
            onChange={handleChange}
            placeholder="e.g. Software Engineer"
            disabled={isLoadingProfile}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Company Name"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              placeholder="e.g. Acme Inc."
              disabled={isLoadingProfile}
            />
            <Input
              label="Business Unit"
              name="businessUnit"
              value={formData.businessUnit}
              onChange={handleChange}
              placeholder="e.g. Engineering"
              disabled={isLoadingProfile}
            />
          </div>

          <div className="w-full">
            <label className="label">Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Additional notes..."
              disabled={isLoadingProfile}
              rows={4}
              className="input w-full resize-none"
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              isLoading={isSaving}
              disabled={emailValidation.status === 'invalid' || emailValidation.status === 'checking'}
            >
              {t('common.save')}
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
};

export default ProfileSettings;
