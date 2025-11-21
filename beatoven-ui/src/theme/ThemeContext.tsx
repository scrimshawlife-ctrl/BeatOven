/**
 * Theme Context - Dark/Light theme switching
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const THEME_KEY = '@beatoven/theme';

// Dark theme (default)
export const darkColors = {
  background: '#0D0D0D',
  surface: '#1A1A1A',
  surfaceLight: '#252525',
  surfaceLighter: '#333333',
  textPrimary: '#FFFFFF',
  textSecondary: '#B0B0B0',
  textMuted: '#666666',
  accent: '#00D9FF',
  accentDark: '#00A8C6',
  accentLight: '#66E8FF',
  success: '#00FF88',
  warning: '#FFB800',
  error: '#FF4444',
  rhythm: '#FF6B6B',
  harmony: '#4ECDC4',
  timbre: '#FFE66D',
  motion: '#C44DFF',
  stems: '#00D9FF',
  border: '#333333',
  borderLight: '#444444',
};

// Light theme
export const lightColors = {
  background: '#F5F5F5',
  surface: '#FFFFFF',
  surfaceLight: '#EEEEEE',
  surfaceLighter: '#E0E0E0',
  textPrimary: '#1A1A1A',
  textSecondary: '#666666',
  textMuted: '#999999',
  accent: '#0099CC',
  accentDark: '#007799',
  accentLight: '#33BBEE',
  success: '#00AA55',
  warning: '#CC8800',
  error: '#DD3333',
  rhythm: '#DD5555',
  harmony: '#33AA99',
  timbre: '#CCAA00',
  motion: '#9933CC',
  stems: '#0099CC',
  border: '#DDDDDD',
  borderLight: '#CCCCCC',
};

export type ThemeMode = 'dark' | 'light';
export type ThemeColors = typeof darkColors;

interface ThemeContextValue {
  mode: ThemeMode;
  colors: ThemeColors;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>('dark');

  // Load saved theme
  useEffect(() => {
    AsyncStorage.getItem(THEME_KEY).then((savedMode) => {
      if (savedMode === 'light' || savedMode === 'dark') {
        setMode(savedMode);
      }
    });
  }, []);

  const setTheme = async (newMode: ThemeMode) => {
    setMode(newMode);
    await AsyncStorage.setItem(THEME_KEY, newMode);
  };

  const toggleTheme = () => {
    setTheme(mode === 'dark' ? 'light' : 'dark');
  };

  const colors = mode === 'dark' ? darkColors : lightColors;

  return (
    <ThemeContext.Provider
      value={{
        mode,
        colors,
        toggleTheme,
        setTheme,
        isDark: mode === 'dark',
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export default ThemeContext;
