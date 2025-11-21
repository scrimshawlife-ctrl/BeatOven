/**
 * App Component Tests
 */

import React from 'react';
import renderer from 'react-test-renderer';

// Mock dependencies
jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }: { children: React.ReactNode }) => children,
  useNavigation: () => ({ navigate: jest.fn() }),
  useRoute: () => ({ params: { moduleType: 'rhythm', jobId: 'test' } }),
  DefaultTheme: { colors: {} },
}));

jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: { children: React.ReactNode }) => children,
    Screen: () => null,
  }),
}));

jest.mock('@react-navigation/native-stack', () => ({
  createNativeStackNavigator: () => ({
    Navigator: ({ children }: { children: React.ReactNode }) => children,
    Screen: () => null,
  }),
}));

jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(() => Promise.resolve(null)),
  setItem: jest.fn(() => Promise.resolve()),
}));

jest.mock('react-native-svg', () => ({
  Svg: 'Svg',
  Rect: 'Rect',
}));

describe('App', () => {
  it('renders without crashing', () => {
    const App = require('../src/App').default;
    const tree = renderer.create(<App />);
    expect(tree).toBeTruthy();
  });
});
