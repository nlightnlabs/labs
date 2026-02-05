import React from 'react';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: 'sm' | 'md';
  id?: string;
}

export const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  size = 'md',
  id,
}) => {
  const toggleId = id || `toggle-${Math.random().toString(36).substr(2, 9)}`;

  const sizeClasses = {
    sm: {
      toggle: 'h-5 w-9',
      thumb: 'h-3 w-3',
      translate: checked ? 'translate-x-5' : 'translate-x-1',
    },
    md: {
      toggle: 'h-6 w-11',
      thumb: 'h-4 w-4',
      translate: checked ? 'translate-x-6' : 'translate-x-1',
    },
  };

  const classes = sizeClasses[size];

  return (
    <label
      htmlFor={toggleId}
      className={`inline-flex items-center ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <button
        id={toggleId}
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`
          relative inline-flex items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
          ${classes.toggle}
          ${checked ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'}
        `}
      >
        <span
          className={`
            inline-block rounded-full bg-white shadow transform transition-transform duration-200
            ${classes.thumb}
            ${classes.translate}
          `}
        />
      </button>
      {label && (
        <span className="ml-3 text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
          {label}
        </span>
      )}
    </label>
  );
};

export default Toggle;
