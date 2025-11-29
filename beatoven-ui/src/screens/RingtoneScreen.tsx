/**
 * Ringtone Screen - Generate ringtones and notifications
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { colors, spacing, borderRadius, typography } from '../theme';
import SliderControl from '../components/SliderControl';
import ToggleControl from '../components/ToggleControl';
import { useBackend } from '../hooks/useBackend';

type RingtoneType = 'notification' | 'short_ringtone' | 'standard_ringtone';

interface RingtoneConfig {
  duration_seconds: number;
  ringtone_type: RingtoneType;
  melodic: boolean;
  percussive: boolean;
  intensity: number;
  loop_seamless: boolean;
}

export default function RingtoneScreen() {
  const { apiCall, isLoading } = useBackend();

  const [ringtoneType, setRingtoneType] = useState<RingtoneType>('standard_ringtone');
  const [config, setConfig] = useState<RingtoneConfig>({
    duration_seconds: 25,
    ringtone_type: 'standard_ringtone',
    melodic: true,
    percussive: true,
    intensity: 0.7,
    loop_seamless: true,
  });

  const [generatedRingtone, setGeneratedRingtone] = useState<any | null>(null);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const result = await apiCall<any>('/ringtone/generate', {
        method: 'POST',
        body: JSON.stringify(config),
      });

      setGeneratedRingtone(result);
      Alert.alert('Success', `Ringtone generated: ${result.duration.toFixed(1)}s`);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate ringtone');
      console.error('Ringtone generation failed:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleTypeChange = (type: RingtoneType) => {
    setRingtoneType(type);
    const durations = {
      notification: 2,
      short_ringtone: 12,
      standard_ringtone: 25,
    };
    setConfig({
      ...config,
      ringtone_type: type,
      duration_seconds: durations[type],
    });
  };

  const durationLimits = {
    notification: { min: 1, max: 5 },
    short_ringtone: { min: 10, max: 15 },
    standard_ringtone: { min: 20, max: 30 },
  };

  const currentLimits = durationLimits[ringtoneType];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Ringtone Generator</Text>
        <Text style={styles.subtitle}>Create custom ringtones and notifications</Text>
      </View>

      {/* Type Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Type</Text>
        <View style={styles.typeButtons}>
          {[
            { key: 'notification' as RingtoneType, label: 'Notification', duration: '1-5s' },
            { key: 'short_ringtone' as RingtoneType, label: 'Short', duration: '10-15s' },
            { key: 'standard_ringtone' as RingtoneType, label: 'Standard', duration: '20-30s' },
          ].map((type) => (
            <TouchableOpacity
              key={type.key}
              style={[
                styles.typeButton,
                ringtoneType === type.key && styles.typeButtonActive,
              ]}
              onPress={() => handleTypeChange(type.key)}
            >
              <Text
                style={[
                  styles.typeText,
                  ringtoneType === type.key && styles.typeTextActive,
                ]}
              >
                {type.label}
              </Text>
              <Text style={styles.typeDuration}>{type.duration}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Configuration */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Configuration</Text>

        <SliderControl
          label="Duration"
          value={(config.duration_seconds - currentLimits.min) / (currentLimits.max - currentLimits.min)}
          onValueChange={(v) =>
            setConfig({
              ...config,
              duration_seconds: currentLimits.min + v * (currentLimits.max - currentLimits.min),
            })
          }
          valueDisplay={`${config.duration_seconds.toFixed(1)}s`}
          color={colors.accent}
        />

        <SliderControl
          label="Intensity"
          value={config.intensity}
          onValueChange={(v) => setConfig({ ...config, intensity: v })}
          valueDisplay={`${Math.round(config.intensity * 100)}%`}
          color={colors.accent}
        />

        <ToggleControl
          label="Melodic"
          description="Include melodic elements"
          value={config.melodic}
          onValueChange={(v) => setConfig({ ...config, melodic: v })}
        />

        <ToggleControl
          label="Percussive"
          description="Include rhythmic elements"
          value={config.percussive}
          onValueChange={(v) => setConfig({ ...config, percussive: v })}
        />

        {ringtoneType !== 'notification' && (
          <ToggleControl
            label="Seamless Loop"
            description="Loop without gaps"
            value={config.loop_seamless}
            onValueChange={(v) => setConfig({ ...config, loop_seamless: v })}
          />
        )}
      </View>

      {/* Generate Button */}
      <TouchableOpacity
        style={[styles.generateButton, generating && styles.generateButtonDisabled]}
        onPress={handleGenerate}
        disabled={generating || isLoading}
      >
        {generating ? (
          <ActivityIndicator color={colors.background} />
        ) : (
          <Text style={styles.generateText}>Generate</Text>
        )}
      </TouchableOpacity>

      {/* Generated Ringtone Info */}
      {generatedRingtone && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Generated Ringtone</Text>
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Duration:</Text>
            <Text style={styles.resultValue}>
              {generatedRingtone.duration.toFixed(2)}s
            </Text>
          </View>
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Sample Rate:</Text>
            <Text style={styles.resultValue}>{generatedRingtone.sample_rate} Hz</Text>
          </View>
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Type:</Text>
            <Text style={styles.resultValue}>{generatedRingtone.ringtone_type}</Text>
          </View>
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Provenance:</Text>
            <Text style={styles.resultValue}>{generatedRingtone.provenance_hash}</Text>
          </View>

          <TouchableOpacity style={styles.downloadButton}>
            <Text style={styles.downloadText}>Download</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Presets */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Presets</Text>
        <View style={styles.presetsGrid}>
          {[
            { name: 'Subtle Ping', intensity: 0.4, melodic: true, percussive: false },
            { name: 'Bold Alert', intensity: 0.8, melodic: true, percussive: true },
            { name: 'Minimal Chime', intensity: 0.5, melodic: true, percussive: false },
            { name: 'Rhythm Only', intensity: 0.7, melodic: false, percussive: true },
          ].map((preset) => (
            <TouchableOpacity
              key={preset.name}
              style={styles.presetButton}
              onPress={() =>
                setConfig({
                  ...config,
                  intensity: preset.intensity,
                  melodic: preset.melodic,
                  percussive: preset.percussive,
                })
              }
            >
              <Text style={styles.presetText}>{preset.name}</Text>
            </TouchableOpacity>
          ))}
        </View>
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
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  typeButtons: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  typeButton: {
    flex: 1,
    backgroundColor: colors.surface,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  typeText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  typeTextActive: {
    color: colors.background,
  },
  typeDuration: {
    ...typography.caption,
    color: colors.textMuted,
    fontSize: 10,
  },
  generateButton: {
    backgroundColor: colors.accent,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  generateButtonDisabled: {
    backgroundColor: colors.surfaceLight,
  },
  generateText: {
    ...typography.body,
    color: colors.background,
    fontWeight: '600',
  },
  resultCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  resultTitle: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.md,
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  resultLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  resultValue: {
    ...typography.mono,
    color: colors.textPrimary,
    fontSize: 12,
  },
  downloadButton: {
    backgroundColor: colors.surfaceLight,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  downloadText: {
    ...typography.bodySmall,
    color: colors.accent,
    fontWeight: '500',
  },
  presetsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  presetButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  presetText: {
    ...typography.caption,
    color: colors.textPrimary,
  },
});
