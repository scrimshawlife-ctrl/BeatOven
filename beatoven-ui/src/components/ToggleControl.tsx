/**
 * ToggleControl - Simple toggle switch with label
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Switch,
} from 'react-native';
import { colors, spacing, typography } from '../theme';

interface ToggleControlProps {
  label: string;
  description?: string;
  value: boolean;
  onValueChange: (value: boolean) => void;
  disabled?: boolean;
}

export default function ToggleControl({
  label,
  description,
  value,
  onValueChange,
  disabled = false,
}: ToggleControlProps) {
  return (
    <View style={[styles.container, disabled && styles.containerDisabled]}>
      <View style={styles.textContainer}>
        <Text style={styles.label}>{label}</Text>
        {description && <Text style={styles.description}>{description}</Text>}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        disabled={disabled}
        trackColor={{ false: colors.surface, true: colors.accent }}
        thumbColor={value ? colors.background : colors.textMuted}
        ios_backgroundColor={colors.surface}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  containerDisabled: {
    opacity: 0.5,
  },
  textContainer: {
    flex: 1,
    marginRight: spacing.md,
  },
  label: {
    ...typography.body,
    color: colors.textPrimary,
  },
  description: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: 2,
  },
});
