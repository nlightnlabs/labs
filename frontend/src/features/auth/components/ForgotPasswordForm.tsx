import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button, Input, Alert } from '@/components/common';
import { authApi } from '@/services/api';

export const ForgotPasswordForm: React.FC = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError(t('auth.errors.emailRequired'));
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError(t('auth.errors.emailInvalid'));
      return;
    }

    setIsLoading(true);

    try {
      await authApi.forgotPassword({ email });
      setIsSubmitted(true);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } } };
      setError(error.response?.data?.message || t('errors.general'));
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-12" style={{ backgroundColor: 'var(--bg-page)' }}>
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-success-100 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {t('auth.resetEmailSent')}
            </h2>
            <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
              {t('auth.checkEmail')}
            </p>
          </div>

          <div className="card text-center">
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
              Didn't receive the email? Check your spam folder or try again.
            </p>
            <Button variant="outline" onClick={() => setIsSubmitted(false)}>
              Try Again
            </Button>
          </div>

          <div className="text-center">
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              {t('auth.backToLogin')}
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12" style={{ backgroundColor: 'var(--bg-page)' }}>
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="w-16 h-16 rounded-xl bg-primary-600 flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">S</span>
          </div>
          <h2 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
            {t('auth.resetPassword')}
          </h2>
          <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
            Enter your email and we'll send you a reset link
          </p>
        </div>

        <div className="card">
          {error && (
            <Alert variant="error" className="mb-4" onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label={t('auth.email')}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />

            <Button type="submit" fullWidth isLoading={isLoading}>
              {t('auth.sendResetLink')}
            </Button>
          </form>
        </div>

        <div className="text-center">
          <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
            {t('auth.backToLogin')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;
