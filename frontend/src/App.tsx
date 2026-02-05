import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from './store';
import { useAppSelector, useAppDispatch } from './store/hooks';
import { selectThemeClass } from './store/slices/themeSlice';
import { initializeTenant } from './store/slices/tenantSlice';

// Layout
import { Layout } from './components/layout';

// Auth Pages
import { LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm } from './features/auth/components';

// Feature Pages
import { Dashboard } from './features/dashboard/components';
import { Settings } from './features/settings/components';
import { App1Module, App2Module, App3Module } from './features/applications/components';
import { DataPage } from './features/applications/components/DataPage';

// i18n
import './i18n';

// Styles
import './styles/index.css';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirects to dashboard if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// All available theme classes
const themeClasses = ['light', 'dark', 'ocean', 'forest', 'blossom', 'sunset'];

// Tenant Initializer Component
const TenantInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Initialize tenant on app load
    dispatch(initializeTenant())
      .unwrap()
      .then((config) => {
        console.log('[App] Tenant initialization complete:', config.tenant_name);
      })
      .catch((err) => {
        console.error('[App] Tenant initialization failed:', err);
      });
  }, [dispatch]);

  // Render children immediately since the app can function
  // while tenant config is being fetched
  return <>{children}</>;
};

// Theme Provider Component
const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const themeClass = useAppSelector(selectThemeClass);

  useEffect(() => {
    // Remove all theme classes first
    themeClasses.forEach((cls) => {
      document.documentElement.classList.remove(cls);
    });
    // Apply the current theme class
    document.documentElement.classList.add(themeClass);
  }, [themeClass]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const themeMode = store.getState().theme.mode;
      if (themeMode === 'system') {
        // Remove all theme classes first
        themeClasses.forEach((cls) => {
          document.documentElement.classList.remove(cls);
        });
        // Apply the system preference
        if (mediaQuery.matches) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.add('light');
        }
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return <>{children}</>;
};

// App Routes Component
const AppRoutes: React.FC = () => {
  return (
    <ThemeProvider>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginForm />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterForm />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPasswordForm />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <PublicRoute>
              <ResetPasswordForm />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="data" element={<DataPage appName="data" />} />
          <Route path="settings" element={<Settings />} />
          <Route path="settings/:tab" element={<Settings />} />
          <Route path="app1/*" element={<App1Module />} />
          <Route path="app2/*" element={<App2Module />} />
          <Route path="app3/*" element={<App3Module />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BrowserRouter>
          <TenantInitializer>
            <AppRoutes />
          </TenantInitializer>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  );
};

export default App;
