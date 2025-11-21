/**
 * Home Screen - Quick generate and recent renders
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  FlatList,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, spacing, borderRadius, typography } from '../theme';
import { useBackend, GenerationResult } from '../hooks/useBackend';
import type { RootStackParamList } from '../navigation';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

interface RecentRender {
  job_id: string;
  timestamp: number;
  intent: string;
  fields: {
    resonance: number;
    density: number;
    tension: number;
  };
}

export default function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const { generate, isLoading, error } = useBackend();

  const [intent, setIntent] = useState('');
  const [recentRenders, setRecentRenders] = useState<RecentRender[]>([
    {
      job_id: 'demo_001',
      timestamp: Date.now() - 3600000,
      intent: 'dark ambient pad with subtle rhythm',
      fields: { resonance: 0.7, density: 0.4, tension: 0.5 },
    },
    {
      job_id: 'demo_002',
      timestamp: Date.now() - 7200000,
      intent: 'upbeat electronic groove',
      fields: { resonance: 0.5, density: 0.8, tension: 0.3 },
    },
  ]);
  const [lastResult, setLastResult] = useState<GenerationResult | null>(null);

  const handleGenerate = useCallback(async () => {
    if (!intent.trim()) return;

    try {
      const result = await generate({
        text_intent: intent,
        duration: 16,
        stem_types: ['drums', 'bass', 'pads'],
      });

      setLastResult(result);
      setRecentRenders((prev) => [
        {
          job_id: result.job_id,
          timestamp: Date.now(),
          intent,
          fields: result.fields,
        },
        ...prev.slice(0, 9),
      ]);

      navigation.navigate('Stems', { jobId: result.job_id });
    } catch (err) {
      console.error('Generation failed:', err);
    }
  }, [intent, generate, navigation]);

  const renderRecentItem = ({ item }: { item: RecentRender }) => (
    <TouchableOpacity
      style={styles.recentItem}
      onPress={() => navigation.navigate('Stems', { jobId: item.job_id })}
    >
      <Text style={styles.recentIntent} numberOfLines={1}>
        {item.intent}
      </Text>
      <View style={styles.recentMeta}>
        <Text style={styles.recentField}>
          R:{item.fields.resonance.toFixed(1)}
        </Text>
        <Text style={styles.recentField}>
          D:{item.fields.density.toFixed(1)}
        </Text>
        <Text style={styles.recentField}>
          T:{item.fields.tension.toFixed(1)}
        </Text>
      </View>
      <Text style={styles.recentTime}>
        {new Date(item.timestamp).toLocaleTimeString()}
      </Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>BeatOven</Text>
        <Text style={styles.subtitle}>Generative Music Engine</Text>
      </View>

      {/* Quick Generate */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Generate</Text>
        <TextInput
          style={styles.input}
          placeholder="Describe your music..."
          placeholderTextColor={colors.textMuted}
          value={intent}
          onChangeText={setIntent}
          multiline
          numberOfLines={3}
        />
        <TouchableOpacity
          style={[styles.generateButton, !intent.trim() && styles.buttonDisabled]}
          onPress={handleGenerate}
          disabled={isLoading || !intent.trim()}
        >
          {isLoading ? (
            <ActivityIndicator color={colors.background} />
          ) : (
            <Text style={styles.buttonText}>Generate Beat</Text>
          )}
        </TouchableOpacity>

        {error && <Text style={styles.error}>{error}</Text>}
      </View>

      {/* Quick Presets */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Presets</Text>
        <View style={styles.presetGrid}>
          {[
            { name: 'Dark Ambient', intent: 'dark ambient pad with deep bass' },
            { name: 'Tech House', intent: 'driving tech house groove' },
            { name: 'Chill Lo-Fi', intent: 'relaxed lo-fi hip hop beat' },
            { name: 'Cinematic', intent: 'epic cinematic orchestra' },
          ].map((preset) => (
            <TouchableOpacity
              key={preset.name}
              style={styles.presetButton}
              onPress={() => setIntent(preset.intent)}
            >
              <Text style={styles.presetText}>{preset.name}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Renders */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Renders</Text>
        {recentRenders.length === 0 ? (
          <Text style={styles.emptyText}>No recent renders</Text>
        ) : (
          <FlatList
            data={recentRenders}
            renderItem={renderRecentItem}
            keyExtractor={(item) => item.job_id}
            scrollEnabled={false}
          />
        )}
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
    marginBottom: spacing.xl,
    alignItems: 'center',
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
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
  input: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    color: colors.textPrimary,
    ...typography.body,
    minHeight: 80,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: colors.border,
  },
  generateButton: {
    backgroundColor: colors.accent,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  buttonDisabled: {
    backgroundColor: colors.surfaceLighter,
  },
  buttonText: {
    ...typography.body,
    color: colors.background,
    fontWeight: '600',
  },
  error: {
    ...typography.bodySmall,
    color: colors.error,
    marginTop: spacing.sm,
  },
  presetGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  presetButton: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  presetText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
  },
  recentItem: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  recentIntent: {
    ...typography.body,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  recentMeta: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  recentField: {
    ...typography.mono,
    color: colors.accent,
    fontSize: 12,
  },
  recentTime: {
    ...typography.caption,
    color: colors.textMuted,
  },
  emptyText: {
    ...typography.body,
    color: colors.textMuted,
    textAlign: 'center',
    padding: spacing.lg,
  },
});
