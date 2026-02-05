import React from 'react';

interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses: Record<string, string> = {
  sm: 'avatar-sm text-xs',
  md: 'avatar-md text-sm',
  lg: 'avatar-lg text-base',
  xl: 'avatar-xl text-lg',
};

const getInitials = (name: string): string => {
  const parts = name.split(' ').filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  name,
  size = 'md',
  className = '',
}) => {
  const [imageError, setImageError] = React.useState(false);

  if (src && !imageError) {
    return (
      <img
        src={src}
        alt={alt || name || 'Avatar'}
        className={`avatar ${sizeClasses[size]} ${className}`}
        onError={() => setImageError(true)}
      />
    );
  }

  return (
    <div
      className={`avatar ${sizeClasses[size]} flex items-center justify-center font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 ${className}`}
      aria-label={alt || name || 'Avatar'}
    >
      {name ? getInitials(name) : '?'}
    </div>
  );
};

interface AvatarGroupProps {
  children: React.ReactNode;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  children,
  max = 4,
  size = 'md',
}) => {
  const childArray = React.Children.toArray(children);
  const visibleAvatars = childArray.slice(0, max);
  const remainingCount = childArray.length - max;

  return (
    <div className="flex -space-x-2">
      {visibleAvatars.map((child, index) => (
        <div key={index} className="ring-2 ring-white dark:ring-gray-800 rounded-full">
          {child}
        </div>
      ))}
      {remainingCount > 0 && (
        <div
          className={`avatar ${sizeClasses[size]} flex items-center justify-center font-medium bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300 ring-2 ring-white dark:ring-gray-800`}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
};

export default Avatar;
