/**
 * BeatOven UI Theme
 * Dark, high-contrast, geometric design language
 */

export const colors = {
  // Base
  background: '#0D0D0D',
  surface: '#1A1A1A',
  surfaceLight: '#252525',
  surfaceLighter: '#333333',

  // Text
  textPrimary: '#FFFFFF',
  textSecondary: '#B0B0B0',
  textMuted: '#666666',

  // Accent (single highlight color)
  accent: '#00D9FF',
  accentDark: '#00A8C6',
  accentLight: '#66E8FF',

  // Semantic
  success: '#00FF88',
  warning: '#FFB800',
  error: '#FF4444',

  // Module colors
  rhythm: '#FF6B6B',
  harmony: '#4ECDC4',
  timbre: '#FFE66D',
  motion: '#C44DFF',
  stems: '#00D9FF',

  // Borders
  border: '#333333',
  borderLight: '#444444',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 9999,
};

export const typography = {
  h1: {
    fontSize: 28,
    fontWeight: '700' as const,
    lineHeight: 36,
  },
  h2: {
    fontSize: 22,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  h3: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 22,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16,
  },
  mono: {
    fontSize: 14,
    fontWeight: '500' as const,
    fontFamily: 'monospace',
  },
};

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 8,
  },
};

export const theme = {
  colors,
  spacing,
  borderRadius,
  typography,
  shadows,
};

export type Theme = typeof theme;
export default theme;
