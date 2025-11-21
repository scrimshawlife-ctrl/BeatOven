/**
 * Symbolic Panel Screen - Live display of ABX-Runes fields
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { colors, spacing, borderRadius, typography } from '../theme';

interface SymbolicFields {
  resonance: number;
  density: number;
  drift: number;
  tension: number;
  contrast: number;
  hSigma: number | null; // Emotional index from PsyFi
}

export default function SymbolicPanelScreen() {
  const [fields, setFields] = useState<SymbolicFields>({
    resonance: 0.65,
    density: 0.42,
    drift: 0.38,
    tension: 0.55,
    contrast: 0.48,
    hSigma: 0.72,
  });

  // Simulate live updates
  useEffect(() => {
    const interval = setInterval(() => {
      setFields((prev) => ({
        resonance: Math.max(0, Math.min(1, prev.resonance + (Math.random() - 0.5) * 0.02)),
        density: Math.max(0, Math.min(1, prev.density + (Math.random() - 0.5) * 0.02)),
        drift: Math.max(0, Math.min(1, prev.drift + (Math.random() - 0.5) * 0.02)),
        tension: Math.max(0, Math.min(1, prev.tension + (Math.random() - 0.5) * 0.02)),
        contrast: Math.max(0, Math.min(1, prev.contrast + (Math.random() - 0.5) * 0.02)),
        hSigma: prev.hSigma !== null
          ? Math.max(0, Math.min(1, prev.hSigma + (Math.random() - 0.5) * 0.01))
          : null,
      }));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const renderBar = (value: number, color: string) => (
    <View style={styles.barContainer}>
      <View style={[styles.barFill, { width: `${value * 100}%`, backgroundColor: color }]} />
      <View style={[styles.barBackground]} />
    </View>
  );

  const renderDial = (value: number, label: string, color: string) => {
    const angle = -135 + value * 270; // -135 to 135 degrees
    return (
      <View style={styles.dial}>
        <View style={styles.dialOuter}>
          <View
            style={[
              styles.dialNeedle,
              { transform: [{ rotate: `${angle}deg` }] },
            ]}
          >
            <View style={[styles.dialNeedleTip, { backgroundColor: color }]} />
          </View>
          <View style={styles.dialCenter} />
        </View>
        <Text style={styles.dialValue}>{(value * 100).toFixed(0)}</Text>
        <Text style={styles.dialLabel}>{label}</Text>
      </View>
    );
  };

  const fieldColors = {
    resonance: colors.rhythm,
    density: colors.harmony,
    drift: colors.timbre,
    tension: colors.motion,
    contrast: colors.accent,
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Symbolic Fields</Text>
        <Text style={styles.subtitle}>ABX-Runes Parameters</Text>
      </View>

      {/* Main Fields - Bars */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Current State</Text>
        {(Object.entries(fields) as [keyof typeof fields, number | null][])
          .filter(([key]) => key !== 'hSigma')
          .map(([key, value]) => (
            <View key={key} style={styles.fieldRow}>
              <View style={styles.fieldHeader}>
                <Text style={styles.fieldName}>{key}</Text>
                <Text style={[styles.fieldValue, { color: fieldColors[key as keyof typeof fieldColors] }]}>
                  {(value as number).toFixed(2)}
                </Text>
              </View>
              {renderBar(value as number, fieldColors[key as keyof typeof fieldColors])}
            </View>
          ))}
      </View>

      {/* Dials View */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Dial View</Text>
        <View style={styles.dialsContainer}>
          {renderDial(fields.resonance, 'RES', fieldColors.resonance)}
          {renderDial(fields.density, 'DEN', fieldColors.density)}
          {renderDial(fields.drift, 'DRF', fieldColors.drift)}
          {renderDial(fields.tension, 'TEN', fieldColors.tension)}
          {renderDial(fields.contrast, 'CON', fieldColors.contrast)}
        </View>
      </View>

      {/* Emotional Index (PsyFi) */}
      {fields.hSigma !== null && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Emotional Index (Hσ)</Text>
          <View style={styles.emotionalCard}>
            <View style={styles.emotionalHeader}>
              <Text style={styles.emotionalLabel}>PsyFi Integration</Text>
              <Text style={styles.emotionalValue}>{fields.hSigma.toFixed(3)}</Text>
            </View>
            <View style={styles.emotionalBarContainer}>
              <View
                style={[
                  styles.emotionalBarFill,
                  { width: `${fields.hSigma * 100}%` },
                ]}
              />
            </View>
            <View style={styles.emotionalScale}>
              <Text style={styles.scaleLabel}>Calm</Text>
              <Text style={styles.scaleLabel}>Neutral</Text>
              <Text style={styles.scaleLabel}>Intense</Text>
            </View>
          </View>
        </View>
      )}

      {/* Field Descriptions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Field Reference</Text>
        <View style={styles.referenceCard}>
          {[
            { name: 'Resonance', desc: 'Harmonic richness and sustain' },
            { name: 'Density', desc: 'Event density and complexity' },
            { name: 'Drift', desc: 'Temporal variation and evolution' },
            { name: 'Tension', desc: 'Harmonic/rhythmic tension level' },
            { name: 'Contrast', desc: 'Dynamic range and variation' },
          ].map((field) => (
            <View key={field.name} style={styles.referenceRow}>
              <Text style={styles.referenceName}>{field.name}</Text>
              <Text style={styles.referenceDesc}>{field.desc}</Text>
            </View>
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
  fieldRow: {
    marginBottom: spacing.md,
  },
  fieldHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  fieldName: {
    ...typography.body,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  fieldValue: {
    ...typography.mono,
    fontSize: 14,
  },
  barContainer: {
    height: 8,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.sm,
    overflow: 'hidden',
    position: 'relative',
  },
  barFill: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    borderRadius: borderRadius.sm,
  },
  barBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'transparent',
  },
  dialsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    gap: spacing.md,
  },
  dial: {
    alignItems: 'center',
    width: 60,
  },
  dialOuter: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: colors.surface,
    borderWidth: 2,
    borderColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  dialNeedle: {
    position: 'absolute',
    width: 2,
    height: 20,
    bottom: '50%',
    transformOrigin: 'bottom',
  },
  dialNeedleTip: {
    width: 4,
    height: 16,
    borderRadius: 2,
    marginLeft: -1,
  },
  dialCenter: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.textMuted,
  },
  dialValue: {
    ...typography.mono,
    color: colors.textPrimary,
    marginTop: spacing.xs,
    fontSize: 12,
  },
  dialLabel: {
    ...typography.caption,
    color: colors.textMuted,
    fontSize: 10,
  },
  emotionalCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  emotionalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  emotionalLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  emotionalValue: {
    ...typography.mono,
    color: colors.accent,
  },
  emotionalBarContainer: {
    height: 12,
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.sm,
    overflow: 'hidden',
    marginBottom: spacing.xs,
  },
  emotionalBarFill: {
    height: '100%',
    backgroundColor: colors.accent,
    borderRadius: borderRadius.sm,
  },
  emotionalScale: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  scaleLabel: {
    ...typography.caption,
    color: colors.textMuted,
    fontSize: 10,
  },
  referenceCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  referenceRow: {
    marginBottom: spacing.sm,
  },
  referenceName: {
    ...typography.bodySmall,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  referenceDesc: {
    ...typography.caption,
    color: colors.textMuted,
  },
});
