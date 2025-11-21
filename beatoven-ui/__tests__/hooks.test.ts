/**
 * Hook Tests
 */

import { renderHook, act } from '@testing-library/react-hooks';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(() => Promise.resolve(null)),
  setItem: jest.fn(() => Promise.resolve()),
}));

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ status: 'ok', version: '1.0.0' }),
  })
) as jest.Mock;

describe('useBackend', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with default backend URL', () => {
    const { useBackend } = require('../src/hooks/useBackend');
    const { result } = renderHook(() => useBackend());

    expect(result.current.backendUrl).toBe('http://localhost:8000');
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('provides API methods', () => {
    const { useBackend } = require('../src/hooks/useBackend');
    const { result } = renderHook(() => useBackend());

    expect(typeof result.current.checkHealth).toBe('function');
    expect(typeof result.current.generate).toBe('function');
    expect(typeof result.current.getPresets).toBe('function');
    expect(typeof result.current.translate).toBe('function');
    expect(typeof result.current.generateRhythm).toBe('function');
    expect(typeof result.current.generateHarmony).toBe('function');
    expect(typeof result.current.getPatchbayFlow).toBe('function');
    expect(typeof result.current.getStemUrl).toBe('function');
    expect(typeof result.current.getRunicSignature).toBe('function');
    expect(typeof result.current.getRecentGenerations).toBe('function');
    expect(typeof result.current.getConfig).toBe('function');
  });

  it('generates correct stem URL', () => {
    const { useBackend } = require('../src/hooks/useBackend');
    const { result } = renderHook(() => useBackend());

    const stemUrl = result.current.getStemUrl('job123', 'drums');
    expect(stemUrl).toBe('http://localhost:8000/stems/job123/drums');
  });
});
