import { configureStore, combineReducers } from '@reduxjs/toolkit';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Import slices
import authReducer from '@/features/auth/slices/authSlice';
import navigationReducer from './slices/navigationSlice';
import themeReducer from './slices/themeSlice';
import notificationsReducer from './slices/notificationsSlice';

// Root reducer
const rootReducer = combineReducers({
  auth: authReducer,
  navigation: navigationReducer,
  theme: themeReducer,
  notifications: notificationsReducer,
});

// Persist configuration
const persistConfig = {
  key: 'saas-app',
  version: 1,
  storage,
  whitelist: ['auth', 'navigation', 'theme'], // Only persist these reducers
  blacklist: ['notifications'], // Don't persist notifications
};

// Create persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Create persistor
export const persistor = persistStore(store);

// Types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
