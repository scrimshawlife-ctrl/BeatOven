/**
 * NodeCard - Module node in PatchBay view
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { colors, spacing, borderRadius, typography, shadows } from '../theme';

interface NodeCardProps {
  name: string;
  color: string;
  inputs: string[];
  outputs: string[];
  isActive?: boolean;
  onPress?: () => void;
}

export default function NodeCard({
  name,
  color,
  inputs,
  outputs,
  isActive = false,
  onPress,
}: NodeCardProps) {
  return (
    <TouchableOpacity
      style={[
        styles.container,
        isActive && styles.containerActive,
        { borderLeftColor: color },
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Input Ports */}
      {inputs.length > 0 && (
        <View style={styles.ports}>
          {inputs.map((input, index) => (
            <View key={index} style={[styles.port, styles.inputPort]}>
              <View style={[styles.portDot, { backgroundColor: color }]} />
            </View>
          ))}
        </View>
      )}

      {/* Node Content */}
      <View style={styles.content}>
        <Text style={[styles.name, { color: isActive ? color : colors.textPrimary }]}>
          {name}
        </Text>
        <View style={styles.meta}>
          <Text style={styles.metaText}>
            {inputs.length > 0 ? `${inputs.length} in` : ''}
            {inputs.length > 0 && outputs.length > 0 ? ' / ' : ''}
            {outputs.length > 0 ? `${outputs.length} out` : ''}
          </Text>
        </View>
      </View>

      {/* Output Ports */}
      {outputs.length > 0 && (
        <View style={[styles.ports, styles.outputPorts]}>
          {outputs.map((output, index) => (
            <View key={index} style={[styles.port, styles.outputPort]}>
              <View style={[styles.portDot, { backgroundColor: color }]} />
            </View>
          ))}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderLeftWidth: 3,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
    minWidth: 70,
    ...shadows.sm,
  },
  containerActive: {
    borderColor: colors.accent,
    backgroundColor: colors.surfaceLight,
  },
  content: {
    alignItems: 'center',
  },
  name: {
    ...typography.bodySmall,
    fontWeight: '600',
    textAlign: 'center',
  },
  meta: {
    marginTop: spacing.xs,
  },
  metaText: {
    ...typography.caption,
    color: colors.textMuted,
    fontSize: 9,
  },
  ports: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  outputPorts: {
    marginTop: spacing.xs,
    marginBottom: 0,
  },
  port: {
    padding: 2,
  },
  inputPort: {},
  outputPort: {},
  portDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
});
