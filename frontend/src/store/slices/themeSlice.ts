import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ThemeState, ThemeMode, CustomThemeColors, ThemeOption } from '@/types';

const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

// Available theme options
export const themeOptions: ThemeOption[] = [
  { id: 'light', name: 'Light', icon: 'sun' },
  { id: 'dark', name: 'Dark', icon: 'moon' },
  { id: 'system', name: 'System', icon: 'monitor' },
  { id: 'ocean', name: 'Ocean', icon: 'palette', color: '#0EA5E9' },
  { id: 'forest', name: 'Forest', icon: 'palette', color: '#22C55E' },
  { id: 'blossom', name: 'Blossom', icon: 'palette', color: '#EC4899' },
  { id: 'sunset', name: 'Sunset', icon: 'palette', color: '#F97316' },
];

const initialState: ThemeState = {
  mode: 'system',
  customColors: undefined,
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setThemeMode: (state, action: PayloadAction<ThemeMode>) => {
      state.mode = action.payload;
    },
    setCustomColors: (state, action: PayloadAction<CustomThemeColors | undefined>) => {
      state.customColors = action.payload;
    },
    toggleTheme: (state) => {
      // Cycle through light -> dark -> system
      if (state.mode === 'light') {
        state.mode = 'dark';
      } else if (state.mode === 'dark') {
        state.mode = 'light';
      } else if (state.mode === 'system') {
        state.mode = getSystemTheme() === 'dark' ? 'light' : 'dark';
      } else {
        // For color themes, toggle between their light/dark variants or default to light
        state.mode = 'light';
      }
    },
    cycleTheme: (state) => {
      const currentIndex = themeOptions.findIndex((t) => t.id === state.mode);
      const nextIndex = (currentIndex + 1) % themeOptions.length;
      state.mode = themeOptions[nextIndex].id;
    },
  },
});

export const { setThemeMode, setCustomColors, toggleTheme, cycleTheme } = themeSlice.actions;

// Selector to get the actual base theme (light or dark)
export const selectActualTheme = (state: { theme?: ThemeState }): 'light' | 'dark' => {
  const mode = state.theme?.mode ?? 'system';
  if (mode === 'system') {
    return getSystemTheme();
  }
  // Color themes are considered "light" mode base
  if (mode === 'ocean' || mode === 'forest' || mode === 'blossom' || mode === 'sunset') {
    return 'light';
  }
  return mode;
};

// Selector to get the theme class to apply
export const selectThemeClass = (state: { theme?: ThemeState }): string => {
  const mode = state.theme?.mode ?? 'system';
  if (mode === 'system') {
    return getSystemTheme();
  }
  return mode;
};

export default themeSlice.reducer;
