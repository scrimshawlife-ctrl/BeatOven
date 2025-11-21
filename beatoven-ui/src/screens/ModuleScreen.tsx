/**
 * Module Detail Screen - Configure module parameters
 */

import React, { useState } from 'react';
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
import ToggleControl from '../components/ToggleControl';
import type { RootStackParamList } from '../navigation';

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

const SCALES = ['major', 'minor', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'locrian'];
const TEXTURES = ['smooth', 'gritty', 'metallic', 'organic', 'digital'];
const PATTERNS = ['euclidean', 'polymetric', 'linear', 'random'];

export default function ModuleScreen() {
  const route = useRoute<ModuleScreenRouteProp>();
  const { moduleType } = route.params;

  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [seed, setSeed] = useState('abc123');

  const moduleConfig = config[moduleType];
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
          {PATTERNS.map((pattern) => (
            <TouchableOpacity
              key={pattern}
              style={[
                styles.optionButton,
                config.rhythm.pattern === pattern && {
                  backgroundColor: moduleColor,
                },
              ]}
              onPress={() => updateConfig('pattern', pattern)}
            >
              <Text
                style={[
                  styles.optionText,
                  config.rhythm.pattern === pattern && styles.optionTextActive,
                ]}
              >
                {pattern}
              </Text>
            </TouchableOpacity>
          ))}
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
            {SCALES.map((scale) => (
              <TouchableOpacity
                key={scale}
                style={[
                  styles.optionButton,
                  config.harmony.scale === scale && {
                    backgroundColor: moduleColor,
                  },
                ]}
                onPress={() => updateConfig('scale', scale)}
              >
                <Text
                  style={[
                    styles.optionText,
                    config.harmony.scale === scale && styles.optionTextActive,
                  ]}
                >
                  {scale}
                </Text>
              </TouchableOpacity>
            ))}
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
          {TEXTURES.map((texture) => (
            <TouchableOpacity
              key={texture}
              style={[
                styles.optionButton,
                config.timbre.texture === texture && {
                  backgroundColor: moduleColor,
                },
              ]}
              onPress={() => updateConfig('texture', texture)}
            >
              <Text
                style={[
                  styles.optionText,
                  config.timbre.texture === texture && styles.optionTextActive,
                ]}
              >
                {texture}
              </Text>
            </TouchableOpacity>
          ))}
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
  optionText: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  optionTextActive: {
    color: colors.background,
    fontWeight: '600',
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
