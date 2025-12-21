/**
 * Backend API hook for BeatOven
 */

import { useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DEFAULT_BACKEND_URL = 'http://localhost:8000';
const BACKEND_URL_KEY = '@beatoven/backend_url';

export interface ABXRunesFields {
  resonance: number;
  density: number;
  drift: number;
  tension: number;
  contrast: number;
}

export interface MoodTag {
  name: string;
  intensity: number;
}

export interface GenerationRequest {
  text_intent: string;
  mood_tags?: MoodTag[];
  seed?: string;
  tempo?: number;
  duration?: number;
  stem_types?: string[];
}

export interface Stem {
  name: string;
  duration: number;
  sample_rate: number;
  channels: number;
  provenance_hash: string;
}

export interface GenerationResult {
  job_id: string;
  provenance_hash: string;
  seed_lineage: string;
  fields: ABXRunesFields;
  stems: Stem[];
  compute_time_ms: number;
}

export interface Preset {
  id: string;
  name: string;
  description: string;
  fields: ABXRunesFields;
  tempo: number;
}

export interface ModuleParams {
  rhythm?: {
    density: number;
    swing: number;
    tempo: number;
  };
  harmony?: {
    scale: string;
    mode: string;
    tension: number;
  };
  timbre?: {
    texture: string;
    brightness: number;
  };
  motion?: {
    lfo_rate: number;
    envelope_attack: number;
  };
}

export interface CapabilityFeature {
  id: string;
  available: boolean;
  reason?: string | null;
}

export interface CapabilityResponse {
  features: CapabilityFeature[];
}

export interface ConfigSchemaOption {
  value: string;
  label: string;
}

export interface ConfigSchemaModule {
  [key: string]: {
    min?: number;
    max?: number;
    default?: number;
    options?: ConfigSchemaOption[];
  };
}

export interface ConfigSchemaResponse {
  version: string;
  modules: Record<string, ConfigSchemaModule>;
}

export function useBackend() {
  const [backendUrl, setBackendUrlState] = useState(DEFAULT_BACKEND_URL);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load saved backend URL
  useEffect(() => {
    AsyncStorage.getItem(BACKEND_URL_KEY).then((url) => {
      if (url) setBackendUrlState(url);
    });
  }, []);

  const setBackendUrl = useCallback(async (url: string) => {
    await AsyncStorage.setItem(BACKEND_URL_KEY, url);
    setBackendUrlState(url);
  }, []);

  const apiCall = useCallback(async <T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      return data as T;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl]);

  // Health check
  const checkHealth = useCallback(async () => {
    return apiCall<{ status: string; version: string }>('/health');
  }, [apiCall]);

  // Generate beat
  const generate = useCallback(async (request: GenerationRequest) => {
    return apiCall<GenerationResult>('/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }, [apiCall]);

  // Get presets
  const getPresets = useCallback(async () => {
    return apiCall<{ presets: Preset[] }>('/presets');
  }, [apiCall]);

  // Translate input to ABX-Runes fields
  const translate = useCallback(async (
    text_intent: string,
    mood_tags?: MoodTag[]
  ) => {
    return apiCall<{ fields: ABXRunesFields }>('/translate', {
      method: 'POST',
      body: JSON.stringify({ text_intent, mood_tags }),
    });
  }, [apiCall]);

  // Get rhythm
  const generateRhythm = useCallback(async (params: ModuleParams['rhythm']) => {
    return apiCall<{ pattern: number[][]; description: string }>('/rhythm', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }, [apiCall]);

  // Get harmony
  const generateHarmony = useCallback(async (params: ModuleParams['harmony']) => {
    return apiCall<{ progression: string[]; description: string }>('/harmony', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }, [apiCall]);

  // Get patchbay flow
  const getPatchbayFlow = useCallback(async () => {
    return apiCall<{ nodes: string[]; connections: [string, string][] }>('/patchbay/flow');
  }, [apiCall]);

  // Get stem audio
  const getStemUrl = useCallback((jobId: string, stemName: string) => {
    return `${backendUrl}/stems/${jobId}/${stemName}`;
  }, [backendUrl]);

  // Get runic signature
  const getRunicSignature = useCallback(async (jobId: string) => {
    return apiCall<{ svg: string; hash: string }>(`/runic/${jobId}`);
  }, [apiCall]);

  // Get recent generations
  const getRecentGenerations = useCallback(async (limit = 10) => {
    return apiCall<{ generations: GenerationResult[] }>(`/generations?limit=${limit}`);
  }, [apiCall]);

  // Get config
  const getConfig = useCallback(async () => {
    return apiCall<Record<string, unknown>>('/config');
  }, [apiCall]);

  const getCapabilities = useCallback(async () => {
    return apiCall<CapabilityResponse>('/api/capabilities');
  }, [apiCall]);

  const getConfigSchema = useCallback(async () => {
    return apiCall<ConfigSchemaResponse>('/api/config/schema');
  }, [apiCall]);

  return {
    backendUrl,
    setBackendUrl,
    isLoading,
    error,
    checkHealth,
    generate,
    getPresets,
    translate,
    generateRhythm,
    generateHarmony,
    getPatchbayFlow,
    getStemUrl,
    getRunicSignature,
    getRecentGenerations,
    getConfig,
    getCapabilities,
    getConfigSchema,
  };
}

export default useBackend;
