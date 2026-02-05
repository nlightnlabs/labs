import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { NavigationState } from '@/types';

const initialState: NavigationState = {
  isCollapsed: false,
  isMobileOpen: false,
  activeItem: null,
};

const navigationSlice = createSlice({
  name: 'navigation',
  initialState,
  reducers: {
    toggleCollapse: (state) => {
      state.isCollapsed = !state.isCollapsed;
    },
    setCollapsed: (state, action: PayloadAction<boolean>) => {
      state.isCollapsed = action.payload;
    },
    toggleMobileNav: (state) => {
      state.isMobileOpen = !state.isMobileOpen;
    },
    openMobileNav: (state) => {
      state.isMobileOpen = true;
    },
    closeMobileNav: (state) => {
      state.isMobileOpen = false;
    },
    setActiveItem: (state, action: PayloadAction<string | null>) => {
      state.activeItem = action.payload;
    },
  },
});

export const {
  toggleCollapse,
  setCollapsed,
  toggleMobileNav,
  openMobileNav,
  closeMobileNav,
  setActiveItem,
} = navigationSlice.actions;

export default navigationSlice.reducer;
