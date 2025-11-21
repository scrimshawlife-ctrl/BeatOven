/**
 * BeatOven Mobile App
 * React Native (Expo) UI for the BeatOven generative music engine
 */

import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Navigation from './navigation';
import ErrorBoundary from './components/ErrorBoundary';
import { ThemeProvider, useTheme } from './theme/ThemeContext';

function AppContent() {
  const { isDark } = useTheme();
  return (
    <SafeAreaProvider>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <Navigation />
    </SafeAreaProvider>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </ErrorBoundary>
  );
}
