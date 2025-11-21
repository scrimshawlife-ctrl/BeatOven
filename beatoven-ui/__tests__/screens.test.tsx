/**
 * Screen Tests
 */

import React from 'react';
import renderer from 'react-test-renderer';

// Mock dependencies
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: jest.fn() }),
  useRoute: () => ({ params: { moduleType: 'rhythm', jobId: 'test_job_123' } }),
}));

jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(() => Promise.resolve(null)),
  setItem: jest.fn(() => Promise.resolve()),
}));

jest.mock('react-native-svg', () => ({
  Svg: 'Svg',
  Rect: 'Rect',
}));

describe('HomeScreen', () => {
  it('renders without crashing', () => {
    const HomeScreen = require('../src/screens/HomeScreen').default;
    const tree = renderer.create(<HomeScreen />);
    expect(tree).toBeTruthy();
  });
});

describe('PatchbayScreen', () => {
  it('renders without crashing', () => {
    const PatchbayScreen = require('../src/screens/PatchbayScreen').default;
    const tree = renderer.create(<PatchbayScreen />);
    expect(tree).toBeTruthy();
  });
});

describe('ModuleScreen', () => {
  it('renders rhythm module', () => {
    jest.doMock('@react-navigation/native', () => ({
      useNavigation: () => ({ navigate: jest.fn() }),
      useRoute: () => ({ params: { moduleType: 'rhythm' } }),
    }));
    const ModuleScreen = require('../src/screens/ModuleScreen').default;
    const tree = renderer.create(<ModuleScreen />);
    expect(tree).toBeTruthy();
  });
});

describe('StemsScreen', () => {
  it('renders without crashing', () => {
    const StemsScreen = require('../src/screens/StemsScreen').default;
    const tree = renderer.create(<StemsScreen />);
    expect(tree).toBeTruthy();
  });
});

describe('SymbolicPanelScreen', () => {
  it('renders without crashing', () => {
    const SymbolicPanelScreen = require('../src/screens/SymbolicPanelScreen').default;
    const tree = renderer.create(<SymbolicPanelScreen />);
    expect(tree).toBeTruthy();
  });
});

describe('SettingsScreen', () => {
  it('renders without crashing', () => {
    const SettingsScreen = require('../src/screens/SettingsScreen').default;
    const tree = renderer.create(<SettingsScreen />);
    expect(tree).toBeTruthy();
  });
});
