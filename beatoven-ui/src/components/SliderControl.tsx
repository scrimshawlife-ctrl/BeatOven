/**
 * SliderControl - Parameter slider with label and value display
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  PanResponder,
  Animated,
} from 'react-native';
import { colors, spacing, borderRadius, typography } from '../theme';

interface SliderControlProps {
  label: string;
  value: number; // 0-1
  onValueChange: (value: number) => void;
  valueDisplay?: string;
  color?: string;
  disabled?: boolean;
}

export default function SliderControl({
  label,
  value,
  onValueChange,
  valueDisplay,
  color = colors.accent,
  disabled = false,
}: SliderControlProps) {
  const [sliderWidth, setSliderWidth] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => !disabled,
    onMoveShouldSetPanResponder: () => !disabled,
    onPanResponderGrant: () => {
      setIsDragging(true);
    },
    onPanResponderMove: (_, gestureState) => {
      if (sliderWidth > 0) {
        const newValue = Math.max(0, Math.min(1, gestureState.moveX / sliderWidth));
        onValueChange(newValue);
      }
    },
    onPanResponderRelease: () => {
      setIsDragging(false);
    },
  });

  const handleLayout = (event: { nativeEvent: { layout: { width: number } } }) => {
    setSliderWidth(event.nativeEvent.layout.width);
  };

  return (
    <View style={[styles.container, disabled && styles.containerDisabled]}>
      <View style={styles.header}>
        <Text style={styles.label}>{label}</Text>
        <Text style={[styles.value, { color }]}>
          {valueDisplay || value.toFixed(2)}
        </Text>
      </View>
      <View
        style={styles.sliderContainer}
        onLayout={handleLayout}
        {...panResponder.panHandlers}
      >
        <View style={styles.track}>
          <View
            style={[
              styles.fill,
              {
                width: `${value * 100}%`,
                backgroundColor: color,
              },
            ]}
          />
        </View>
        <View
          style={[
            styles.thumb,
            {
              left: `${value * 100}%`,
              backgroundColor: color,
              transform: [
                { translateX: -8 },
                { scale: isDragging ? 1.2 : 1 },
              ],
            },
          ]}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  containerDisabled: {
    opacity: 0.5,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  label: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  value: {
    ...typography.mono,
    fontSize: 12,
  },
  sliderContainer: {
    height: 24,
    justifyContent: 'center',
    position: 'relative',
  },
  track: {
    height: 6,
    backgroundColor: colors.surface,
    borderRadius: 3,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 3,
  },
  thumb: {
    position: 'absolute',
    width: 16,
    height: 16,
    borderRadius: 8,
    top: 4,
  },
});
