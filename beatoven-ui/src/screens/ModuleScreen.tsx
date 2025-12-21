/**
 * Module Detail Screen - Configure module parameters
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, spacing, borderRadius, typography } from '../theme';
import SliderControl from '../components/SliderControl';
import type { RootStackParamList } from '../navigation';
import useBackend, { CapabilityResponse, ConfigSchemaResponse } from '../hooks/useBackend';

type ModuleScreenRouteProp = RouteProp<RootStackParamList, 'Module'>;

interface ModuleConfig {
  rhythm: {
    tempo: number;
    swing: number;
    density: number;
    pattern: string;
  };
  harmony: {
    scale: string;
    mode: string;
    tension: number;
    complexity: number;
  };
  timbre: {
    texture: string;
    brightness: number;
    warmth: number;
    reverb: number;
  };
  motion: {
    lfoRate: number;
    lfoDepth: number;
    attack: number;
    decay: number;
  };
}

const DEFAULT_CONFIG: ModuleConfig = {
  rhythm: {
    tempo: 120,
    swing: 0,
    density: 0.5,
    pattern: 'euclidean',
  },
  harmony: {
    scale: 'minor',
    mode: 'aeolian',
    tension: 0.5,
    complexity: 0.5,
  },
  timbre: {
    texture: 'smooth',
    brightness: 0.5,
    warmth: 0.5,
    reverb: 0.3,
  },
  motion: {
    lfoRate: 0.5,
    lfoDepth: 0.3,
    attack: 0.1,
    decay: 0.5,
  },
};

const DEFAULT_SCALES = ['major', 'minor', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'locrian'];
const DEFAULT_TEXTURES = ['smooth', 'gritty', 'metallic', 'organic', 'digital'];
const DEFAULT_PATTERNS = ['euclidean', 'polymetric', 'linear', 'random'];

export default function ModuleScreen() {
  const route = useRoute<ModuleScreenRouteProp>();
  const { moduleType } = route.params;
  const { getCapabilities, getConfigSchema } = useBackend();

  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [seed, setSeed] = useState('abc123');
  const [schema, setSchema] = useState<ConfigSchemaResponse | null>(null);
  const [capabilities, setCapabilities] = useState<CapabilityResponse | null>(null);

  const moduleColor = {
    rhythm: colors.rhythm,
    harmony: colors.harmony,
    timbre: colors.timbre,
    motion: colors.motion,
  }[moduleType];

  const updateConfig = <K extends keyof ModuleConfig[typeof moduleType]>(
    key: K,
    value: ModuleConfig[typeof moduleType][K]
  ) => {
    setConfig((prev) => ({
      ...prev,
      [moduleType]: {
        ...prev[moduleType],
        [key]: value,
      },
    }));
  };

  useEffect(() => {
    const loadSchema = async () => {
      try {
        const [schemaResponse, capabilityResponse] = await Promise.all([
          getConfigSchema(),
          getCapabilities(),
        ]);
        setSchema(schemaResponse);
        setCapabilities(capabilityResponse);
        const moduleSchema = schemaResponse.modules;
        setConfig((prev) => ({
          rhythm: {
            tempo: moduleSchema.rhythm?.tempo?.default ?? prev.rhythm.tempo,
            swing: moduleSchema.rhythm?.swing?.default ?? prev.rhythm.swing,
            density: moduleSchema.rhythm?.density?.default ?? prev.rhythm.density,
            pattern: moduleSchema.rhythm?.pattern?.options?.[0]?.value ?? prev.rhythm.pattern,
          },
          harmony: {
            scale: moduleSchema.harmony?.scale?.options?.[0]?.value ?? prev.harmony.scale,
            mode: prev.harmony.mode,
            tension: moduleSchema.harmony?.tension?.default ?? prev.harmony.tension,
            complexity: moduleSchema.harmony?.complexity?.default ?? prev.harmony.complexity,
          },
          timbre: {
            texture: moduleSchema.timbre?.texture?.options?.[0]?.value ?? prev.timbre.texture,
            brightness: moduleSchema.timbre?.brightness?.default ?? prev.timbre.brightness,
            warmth: moduleSchema.timbre?.warmth?.default ?? prev.timbre.warmth,
            reverb: moduleSchema.timbre?.reverb?.default ?? prev.timbre.reverb,
          },
          motion: {
            lfoRate: moduleSchema.motion?.lfoRate?.default ?? prev.motion.lfoRate,
            lfoDepth: moduleSchema.motion?.lfoDepth?.default ?? prev.motion.lfoDepth,
            attack: moduleSchema.motion?.attack?.default ?? prev.motion.attack,
            decay: moduleSchema.motion?.decay?.default ?? prev.motion.decay,
          },
        }));
      } catch (error) {
        setSchema(null);
        setCapabilities(null);
      }
    };

    loadSchema();
  }, [getCapabilities, getConfigSchema]);

  const featureAvailability = useMemo(() => {
    const featureMap = new Map<string, CapabilityResponse['features'][number]>();
    capabilities?.features.forEach((feature) => featureMap.set(feature.id, feature));
    return featureMap;
  }, [capabilities]);

  const getFeatureStatus = (featureId: string) => {
    return featureAvailability.get(featureId) ?? { id: featureId, available: true };
  };

  const schemaOptions = {
    patterns: schema?.modules.rhythm?.pattern?.options?.map((option) => option.value) ?? DEFAULT_PATTERNS,
    scales: schema?.modules.harmony?.scale?.options?.map((option) => option.value) ?? DEFAULT_SCALES,
    textures: schema?.modules.timbre?.texture?.options?.map((option) => option.value) ?? DEFAULT_TEXTURES,
  };

  const regenerateSeed = () => {
    const chars = 'abcdef0123456789';
    let newSeed = '';
    for (let i = 0; i < 8; i++) {
      newSeed += chars[Math.floor(Math.random() * chars.length)];
    }
    setSeed(newSeed);
  };

  const renderRhythmControls = () => (
    <>
      <SliderControl
        label="Tempo"
        value={(config.rhythm.tempo - 60) / 140}
        onValueChange={(v) => updateConfig('tempo', Math.round(60 + v * 140))}
        valueDisplay={`${config.rhythm.tempo} BPM`}
        color={moduleColor}
      />
      <SliderControl
        label="Swing"
        value={config.rhythm.swing}
        onValueChange={(v) => updateConfig('swing', v)}
        valueDisplay={`${Math.round(config.rhythm.swing * 100)}%`}
        color={moduleColor}
      />
      <SliderControl
        label="Density"
        value={config.rhythm.density}
        onValueChange={(v) => updateConfig('density', v)}
        valueDisplay={config.rhythm.density.toFixed(2)}
        color={moduleColor}
      />
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Pattern</Text>
        <View style={styles.optionButtons}>
          {schemaOptions.patterns.map((pattern) => {
            const feature = getFeatureStatus(`rhythm.pattern.${pattern}`);
            return (
              <TouchableOpacity
                key={pattern}
                style={[
                  styles.optionButton,
                  config.rhythm.pattern === pattern && {
                    backgroundColor: moduleColor,
                  },
                  !feature.available && styles.optionButtonDisabled,
                ]}
                onPress={() => feature.available && updateConfig('pattern', pattern)}
              >
                <Text
                  style={[
                    styles.optionText,
                    config.rhythm.pattern === pattern && styles.optionTextActive,
                    !feature.available && styles.optionTextDisabled,
                  ]}
                >
                  {pattern}
                </Text>
                {!feature.available && feature.reason ? (
                  <Text style={styles.optionReason}>{feature.reason}</Text>
                ) : null}
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </>
  );

  const renderHarmonyControls = () => (
    <>
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Scale</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.optionButtons}>
            {schemaOptions.scales.map((scale) => {
              const feature = getFeatureStatus(`harmony.scale.${scale}`);
              return (
                <TouchableOpacity
                  key={scale}
                  style={[
                    styles.optionButton,
                    config.harmony.scale === scale && {
                      backgroundColor: moduleColor,
                    },
                    !feature.available && styles.optionButtonDisabled,
                  ]}
                  onPress={() => feature.available && updateConfig('scale', scale)}
                >
                  <Text
                    style={[
                      styles.optionText,
                      config.harmony.scale === scale && styles.optionTextActive,
                      !feature.available && styles.optionTextDisabled,
                    ]}
                  >
                    {scale}
                  </Text>
                  {!feature.available && feature.reason ? (
                    <Text style={styles.optionReason}>{feature.reason}</Text>
                  ) : null}
                </TouchableOpacity>
              );
            })}
          </View>
        </ScrollView>
      </View>
      <SliderControl
        label="Tension"
        value={config.harmony.tension}
        onValueChange={(v) => updateConfig('tension', v)}
        valueDisplay={config.harmony.tension.toFixed(2)}
        color={moduleColor}
      />
      <SliderControl
        label="Complexity"
        value={config.harmony.complexity}
        onValueChange={(v) => updateConfig('complexity', v)}
        valueDisplay={config.harmony.complexity.toFixed(2)}
        color={moduleColor}
      />
    </>
  );

  const renderTimbreControls = () => (
    <>
      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Texture</Text>
        <View style={styles.optionButtons}>
          {schemaOptions.textures.map((texture) => {
            const feature = getFeatureStatus(`timbre.texture.${texture}`);
            return (
              <TouchableOpacity
                key={texture}
                style={[
                  styles.optionButton,
                  config.timbre.texture === texture && {
                    backgroundColor: moduleColor,
                  },
                  !feature.available && styles.optionButtonDisabled,
                ]}
                onPress={() => feature.available && updateConfig('texture', texture)}
              >
                <Text
                  style={[
                    styles.optionText,
                    config.timbre.texture === texture && styles.optionTextActive,
                    !feature.available && styles.optionTextDisabled,
                  ]}
                >
                  {texture}
                </Text>
                {!feature.available && feature.reason ? (
                  <Text style={styles.optionReason}>{feature.reason}</Text>
                ) : null}
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
      <SliderControl
        label="Brightness"
        value={config.timbre.brightness}
        onValueChange={(v) => updateConfig('brightness', v)}
        valueDisplay={config.timbre.brightness.toFixed(2)}
        color={moduleColor}
      />
      <SliderControl
        label="Warmth"
        value={config.timbre.warmth}
        onValueChange={(v) => updateConfig('warmth', v)}
        valueDisplay={config.timbre.warmth.toFixed(2)}
        color={moduleColor}
      />
      <SliderControl
        label="Reverb"
        value={config.timbre.reverb}
        onValueChange={(v) => updateConfig('reverb', v)}
        valueDisplay={config.timbre.reverb.toFixed(2)}
        color={moduleColor}
      />
    </>
  );

  const renderMotionControls = () => (
    <>
      <SliderControl
        label="LFO Rate"
        value={config.motion.lfoRate}
        onValueChange={(v) => updateConfig('lfoRate', v)}
        valueDisplay={`${(config.motion.lfoRate * 10).toFixed(1)} Hz`}
        color={moduleColor}
      />
      <SliderControl
        label="LFO Depth"
        value={config.motion.lfoDepth}
        onValueChange={(v) => updateConfig('lfoDepth', v)}
        valueDisplay={config.motion.lfoDepth.toFixed(2)}
        color={moduleColor}
      />
      <SliderControl
        label="Attack"
        value={config.motion.attack}
        onValueChange={(v) => updateConfig('attack', v)}
        valueDisplay={`${(config.motion.attack * 1000).toFixed(0)} ms`}
        color={moduleColor}
      />
      <SliderControl
        label="Decay"
        value={config.motion.decay}
        onValueChange={(v) => updateConfig('decay', v)}
        valueDisplay={`${(config.motion.decay * 1000).toFixed(0)} ms`}
        color={moduleColor}
      />
    </>
  );

  const renderControls = () => {
    switch (moduleType) {
      case 'rhythm':
        return renderRhythmControls();
      case 'harmony':
        return renderHarmonyControls();
      case 'timbre':
        return renderTimbreControls();
      case 'motion':
        return renderMotionControls();
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Module Header */}
      <View style={[styles.header, { borderLeftColor: moduleColor }]}>
        <Text style={styles.title}>{moduleType}</Text>
        <Text style={styles.subtitle}>Configure parameters</Text>
      </View>

      {/* Seed Control */}
      <View style={styles.seedSection}>
        <Text style={styles.seedLabel}>Seed</Text>
        <View style={styles.seedRow}>
          <Text style={styles.seedValue}>{seed}</Text>
          <TouchableOpacity style={styles.seedButton} onPress={regenerateSeed}>
            <Text style={styles.seedButtonText}>Regenerate</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Module Controls */}
      <View style={styles.controls}>{renderControls()}</View>

      {/* Save/Load */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionText}>Save Preset</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionButton, styles.actionSecondary]}>
          <Text style={[styles.actionText, styles.actionTextSecondary]}>
            Load Preset
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.md,
  },
  header: {
    borderLeftWidth: 4,
    paddingLeft: spacing.md,
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
    textTransform: 'capitalize',
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  seedSection: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  seedLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  seedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  seedValue: {
    ...typography.mono,
    color: colors.accent,
    fontSize: 16,
  },
  seedButton: {
    backgroundColor: colors.surfaceLight,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
  },
  seedButtonText: {
    ...typography.caption,
    color: colors.textPrimary,
  },
  controls: {
    gap: spacing.lg,
    marginBottom: spacing.xl,
  },
  optionGroup: {
    marginBottom: spacing.md,
  },
  optionLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  optionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  optionButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  optionButtonDisabled: {
    opacity: 0.5,
  },
  optionText: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  optionTextActive: {
    color: colors.background,
    fontWeight: '600',
  },
  optionTextDisabled: {
    color: colors.textSecondary,
  },
  optionReason: {
    ...typography.caption,
    color: colors.textSecondary,
    fontSize: 10,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.accent,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  actionSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border,
  },
  actionText: {
    ...typography.body,
    color: colors.background,
    fontWeight: '600',
  },
  actionTextSecondary: {
    color: colors.textPrimary,
  },
});
