/**
 * Preset Management Hook
 */

import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const PRESETS_KEY = '@beatoven/presets';

export interface ModulePreset {
  id: string;
  name: string;
  createdAt: number;
  moduleType: 'rhythm' | 'harmony' | 'timbre' | 'motion' | 'global';
  params: Record<string, unknown>;
}

export interface GenerationPreset {
  id: string;
  name: string;
  createdAt: number;
  intent: string;
  moodTags: { name: string; intensity: number }[];
  modulePresets: {
    rhythm?: string;
    harmony?: string;
    timbre?: string;
    motion?: string;
  };
}

interface PresetsState {
  modulePresets: ModulePreset[];
  generationPresets: GenerationPreset[];
}

const defaultState: PresetsState = {
  modulePresets: [],
  generationPresets: [],
};

export function usePresets() {
  const [presets, setPresets] = useState<PresetsState>(defaultState);
  const [isLoading, setIsLoading] = useState(true);

  // Load presets from storage
  useEffect(() => {
    const loadPresets = async () => {
      try {
        const stored = await AsyncStorage.getItem(PRESETS_KEY);
        if (stored) {
          setPresets(JSON.parse(stored));
        }
      } catch (error) {
        console.error('Failed to load presets:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadPresets();
  }, []);

  // Save presets to storage
  const savePresets = useCallback(async (newPresets: PresetsState) => {
    try {
      await AsyncStorage.setItem(PRESETS_KEY, JSON.stringify(newPresets));
      setPresets(newPresets);
    } catch (error) {
      console.error('Failed to save presets:', error);
      throw error;
    }
  }, []);

  // Add module preset
  const addModulePreset = useCallback(
    async (preset: Omit<ModulePreset, 'id' | 'createdAt'>) => {
      const newPreset: ModulePreset = {
        ...preset,
        id: `mp_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
        createdAt: Date.now(),
      };
      const newPresets = {
        ...presets,
        modulePresets: [...presets.modulePresets, newPreset],
      };
      await savePresets(newPresets);
      return newPreset;
    },
    [presets, savePresets]
  );

  // Add generation preset
  const addGenerationPreset = useCallback(
    async (preset: Omit<GenerationPreset, 'id' | 'createdAt'>) => {
      const newPreset: GenerationPreset = {
        ...preset,
        id: `gp_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
        createdAt: Date.now(),
      };
      const newPresets = {
        ...presets,
        generationPresets: [...presets.generationPresets, newPreset],
      };
      await savePresets(newPresets);
      return newPreset;
    },
    [presets, savePresets]
  );

  // Delete module preset
  const deleteModulePreset = useCallback(
    async (id: string) => {
      const newPresets = {
        ...presets,
        modulePresets: presets.modulePresets.filter((p) => p.id !== id),
      };
      await savePresets(newPresets);
    },
    [presets, savePresets]
  );

  // Delete generation preset
  const deleteGenerationPreset = useCallback(
    async (id: string) => {
      const newPresets = {
        ...presets,
        generationPresets: presets.generationPresets.filter((p) => p.id !== id),
      };
      await savePresets(newPresets);
    },
    [presets, savePresets]
  );

  // Get presets by module type
  const getModulePresets = useCallback(
    (moduleType: ModulePreset['moduleType']) => {
      return presets.modulePresets.filter((p) => p.moduleType === moduleType);
    },
    [presets.modulePresets]
  );

  // Update module preset
  const updateModulePreset = useCallback(
    async (id: string, updates: Partial<Omit<ModulePreset, 'id' | 'createdAt'>>) => {
      const newPresets = {
        ...presets,
        modulePresets: presets.modulePresets.map((p) =>
          p.id === id ? { ...p, ...updates } : p
        ),
      };
      await savePresets(newPresets);
    },
    [presets, savePresets]
  );

  // Clear all presets
  const clearAllPresets = useCallback(async () => {
    await savePresets(defaultState);
  }, [savePresets]);

  return {
    modulePresets: presets.modulePresets,
    generationPresets: presets.generationPresets,
    isLoading,
    addModulePreset,
    addGenerationPreset,
    deleteModulePreset,
    deleteGenerationPreset,
    getModulePresets,
    updateModulePreset,
    clearAllPresets,
  };
}

export default usePresets;
