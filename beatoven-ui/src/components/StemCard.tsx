/**
 * StemCard - Audio stem with waveform preview and animated playhead
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';
import Svg, { Rect, Line } from 'react-native-svg';
import { colors, spacing, borderRadius, typography } from '../theme';

interface StemCardProps {
  name: string;
  duration: number;
  waveform: number[];
  color: string;
  isPlaying?: boolean;
  isLoading?: boolean;
  progress?: number; // 0-1 playback progress
  onPlay?: () => void;
  onDownload?: () => void;
}

const AnimatedLine = Animated.createAnimatedComponent(Line);

export default function StemCard({
  name,
  duration,
  waveform,
  color,
  isPlaying = false,
  isLoading = false,
  progress = 0,
  onPlay,
  onDownload,
}: StemCardProps) {
  const playheadAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Animate playhead when playing
  useEffect(() => {
    if (isPlaying) {
      // Reset and start animation
      playheadAnim.setValue(0);
      Animated.timing(playheadAnim, {
        toValue: 200, // width of waveform
        duration: duration * 1000,
        useNativeDriver: false,
      }).start();

      // Pulse animation for play button
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 0.7,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      );
      pulse.start();

      return () => {
        pulse.stop();
        pulseAnim.setValue(1);
      };
    } else {
      playheadAnim.setValue(0);
    }
  }, [isPlaying, duration, playheadAnim, pulseAnim]);

  // Update playhead from external progress
  useEffect(() => {
    if (progress > 0 && isPlaying) {
      playheadAnim.setValue(progress * 200);
    }
  }, [progress, isPlaying, playheadAnim]);

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
      <View style={styles.waveformWrapper}>
        <Svg width={width} height={height} style={styles.waveform}>
          {waveform.map((value, index) => {
            const barHeight = value * height * 0.8;
            const y = (height - barHeight) / 2;
            const barX = index * barWidth;

            return (
              <Rect
                key={index}
                x={barX}
                y={y}
                width={Math.max(1, barWidth - 1)}
                height={barHeight}
                fill={isPlaying ? color : colors.textMuted}
                opacity={isPlaying ? 1 : 0.6}
              />
            );
          })}
        </Svg>
        {/* Playhead overlay */}
        {isPlaying && (
          <Animated.View
            style={[
              styles.playhead,
              {
                left: playheadAnim,
                backgroundColor: color,
              },
            ]}
          />
        )}
      </View>
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
        <Animated.View style={{ flex: 1, opacity: isLoading ? 0.5 : pulseAnim }}>
          <TouchableOpacity
            style={[styles.playButton, isPlaying && { backgroundColor: color }]}
            onPress={onPlay}
            disabled={isLoading}
          >
            <Text style={[styles.buttonText, isPlaying && styles.buttonTextActive]}>
              {isLoading ? 'Loading...' : isPlaying ? 'Stop' : 'Play'}
            </Text>
          </TouchableOpacity>
        </Animated.View>
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
  waveformWrapper: {
    position: 'relative',
    width: 200,
    height: 40,
  },
  waveform: {
    overflow: 'hidden',
  },
  playhead: {
    position: 'absolute',
    top: 0,
    width: 2,
    height: '100%',
    borderRadius: 1,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  playButton: {
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
