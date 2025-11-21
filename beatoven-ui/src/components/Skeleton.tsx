/**
 * Skeleton - Loading placeholder with shimmer effect
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  Animated,
  ViewStyle,
} from 'react-native';
import { colors, borderRadius } from '../theme';

interface SkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export function Skeleton({
  width = '100%',
  height = 20,
  borderRadius: radius = borderRadius.sm,
  style,
}: SkeletonProps) {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 0.6,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );

    animation.start();

    return () => animation.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        styles.skeleton,
        {
          width,
          height,
          borderRadius: radius,
          opacity,
        },
        style,
      ]}
    />
  );
}

export function SkeletonCard({ style }: { style?: ViewStyle }) {
  return (
    <View style={[styles.card, style]}>
      <View style={styles.cardHeader}>
        <Skeleton width={120} height={18} />
        <Skeleton width={60} height={14} />
      </View>
      <Skeleton height={60} borderRadius={borderRadius.md} style={styles.cardBody} />
      <View style={styles.cardFooter}>
        <Skeleton width={80} height={32} borderRadius={borderRadius.sm} />
        <Skeleton width={80} height={32} borderRadius={borderRadius.sm} />
      </View>
    </View>
  );
}

export function SkeletonList({ count = 3, style }: { count?: number; style?: ViewStyle }) {
  return (
    <View style={style}>
      {Array(count)
        .fill(0)
        .map((_, index) => (
          <SkeletonCard key={index} style={index > 0 ? styles.listItem : undefined} />
        ))}
    </View>
  );
}

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: colors.surfaceLight,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardBody: {
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    gap: 8,
  },
  listItem: {
    marginTop: 12,
  },
});

export default Skeleton;
