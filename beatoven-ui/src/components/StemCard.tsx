/**
 * StemCard - Audio stem with waveform preview
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import Svg, { Rect } from 'react-native-svg';
import { colors, spacing, borderRadius, typography } from '../theme';

interface StemCardProps {
  name: string;
  duration: number;
  waveform: number[];
  color: string;
  isPlaying?: boolean;
  onPlay?: () => void;
  onDownload?: () => void;
}

export default function StemCard({
  name,
  duration,
  waveform,
  color,
  isPlaying = false,
  onPlay,
  onDownload,
}: StemCardProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderWaveform = () => {
    const width = 200;
    const height = 40;
    const barWidth = width / waveform.length;

    return (
      <Svg width={width} height={height} style={styles.waveform}>
        {waveform.map((value, index) => {
          const barHeight = value * height * 0.8;
          const y = (height - barHeight) / 2;

          return (
            <Rect
              key={index}
              x={index * barWidth}
              y={y}
              width={Math.max(1, barWidth - 1)}
              height={barHeight}
              fill={isPlaying ? color : colors.textMuted}
              opacity={isPlaying ? 1 : 0.6}
            />
          );
        })}
      </Svg>
    );
  };

  return (
    <View style={[styles.container, { borderLeftColor: color }]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.duration}>{formatDuration(duration)}</Text>
      </View>

      {/* Waveform */}
      <View style={styles.waveformContainer}>
        {renderWaveform()}
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.playButton, isPlaying && { backgroundColor: color }]}
          onPress={onPlay}
        >
          <Text style={[styles.buttonText, isPlaying && styles.buttonTextActive]}>
            {isPlaying ? 'Stop' : 'Play'}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.downloadButton} onPress={onDownload}>
          <Text style={styles.downloadText}>Download</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderLeftWidth: 3,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  name: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  duration: {
    ...typography.mono,
    color: colors.textSecondary,
    fontSize: 12,
  },
  waveformContainer: {
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.sm,
    padding: spacing.sm,
    marginBottom: spacing.md,
    alignItems: 'center',
  },
  waveform: {
    overflow: 'hidden',
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  playButton: {
    flex: 1,
    backgroundColor: colors.surfaceLight,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  buttonTextActive: {
    color: colors.background,
  },
  downloadButton: {
    flex: 1,
    backgroundColor: 'transparent',
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  downloadText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
});
