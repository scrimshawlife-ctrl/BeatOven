/**
 * Stems Screen - Waveform previews and download with audio playback
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import { useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, spacing, borderRadius, typography } from '../theme';
import StemCard from '../components/StemCard';
import { useBackend } from '../hooks/useBackend';
import type { RootStackParamList } from '../navigation';

type StemsScreenRouteProp = RouteProp<RootStackParamList, 'Stems'>;

interface StemData {
  name: string;
  duration: number;
  waveform: number[];
  provenance_hash: string;
  isPlaying: boolean;
}

// Generate mock waveform data
const generateWaveform = (seed: number): number[] => {
  const data: number[] = [];
  let value = 0.5;
  for (let i = 0; i < 100; i++) {
    value += (Math.sin(i * 0.1 + seed) * 0.3 + (Math.random() - 0.5) * 0.2);
    value = Math.max(0.1, Math.min(0.9, value));
    data.push(value);
  }
  return data;
};

export default function StemsScreen() {
  const route = useRoute<StemsScreenRouteProp>();
  const { jobId } = route.params;
  const { getStemUrl } = useBackend();
  const soundRef = useRef<Audio.Sound | null>(null);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
    };
  }, []);

  const [stems, setStems] = useState<StemData[]>([
    {
      name: 'drums',
      duration: 16.0,
      waveform: generateWaveform(1),
      provenance_hash: 'a1b2c3d4e5f6',
      isPlaying: false,
    },
    {
      name: 'bass',
      duration: 16.0,
      waveform: generateWaveform(2),
      provenance_hash: 'f6e5d4c3b2a1',
      isPlaying: false,
    },
    {
      name: 'pads',
      duration: 16.0,
      waveform: generateWaveform(3),
      provenance_hash: '1a2b3c4d5e6f',
      isPlaying: false,
    },
    {
      name: 'leads',
      duration: 16.0,
      waveform: generateWaveform(4),
      provenance_hash: '6f5e4d3c2b1a',
      isPlaying: false,
    },
    {
      name: 'atmos',
      duration: 16.0,
      waveform: generateWaveform(5),
      provenance_hash: 'b1c2d3e4f5a6',
      isPlaying: false,
    },
    {
      name: 'full_mix',
      duration: 16.0,
      waveform: generateWaveform(6),
      provenance_hash: 'c3d4e5f6a7b8',
      isPlaying: false,
    },
  ]);

  const [isExporting, setIsExporting] = useState(false);

  const handlePlay = async (stemName: string) => {
    try {
      // If already playing this stem, stop it
      if (currentlyPlaying === stemName) {
        if (soundRef.current) {
          await soundRef.current.stopAsync();
          await soundRef.current.unloadAsync();
          soundRef.current = null;
        }
        setCurrentlyPlaying(null);
        setStems((prev) =>
          prev.map((s) => ({ ...s, isPlaying: false }))
        );
        return;
      }

      // Stop any currently playing audio
      if (soundRef.current) {
        await soundRef.current.stopAsync();
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }

      setIsLoadingAudio(true);

      // Configure audio mode
      await Audio.setAudioModeAsync({
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
      });

      // Load and play audio from backend
      const url = getStemUrl(jobId, stemName);
      const { sound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: true },
        (status) => {
          if (status.isLoaded && status.didJustFinish) {
            setCurrentlyPlaying(null);
            setStems((prev) =>
              prev.map((s) => ({ ...s, isPlaying: false }))
            );
          }
        }
      );

      soundRef.current = sound;
      setCurrentlyPlaying(stemName);
      setStems((prev) =>
        prev.map((s) => ({
          ...s,
          isPlaying: s.name === stemName,
        }))
      );
    } catch (error) {
      Alert.alert('Playback Error', 'Could not play audio. Make sure the backend is running.');
      console.error('Audio playback error:', error);
    } finally {
      setIsLoadingAudio(false);
    }
  };

  const handleDownload = (stemName: string) => {
    // In real app, would trigger file download
    console.log(`Download stem: ${stemName}`);
  };

  const handleExportAll = async () => {
    setIsExporting(true);
    // Simulate export delay
    setTimeout(() => {
      setIsExporting(false);
    }, 2000);
  };

  const stemColors: Record<string, string> = {
    drums: colors.rhythm,
    bass: colors.harmony,
    pads: colors.timbre,
    leads: colors.motion,
    atmos: colors.accent,
    full_mix: colors.textPrimary,
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Stems</Text>
        <Text style={styles.subtitle}>Job: {jobId}</Text>
      </View>

      {/* Provenance Info */}
      <View style={styles.provenanceCard}>
        <Text style={styles.provenanceLabel}>Generation Provenance</Text>
        <Text style={styles.provenanceHash}>
          sha256:{jobId.slice(0, 8)}...
        </Text>
        <View style={styles.provenanceRow}>
          <View style={styles.provenanceStat}>
            <Text style={styles.statValue}>{stems.length}</Text>
            <Text style={styles.statLabel}>Stems</Text>
          </View>
          <View style={styles.provenanceStat}>
            <Text style={styles.statValue}>16.0s</Text>
            <Text style={styles.statLabel}>Duration</Text>
          </View>
          <View style={styles.provenanceStat}>
            <Text style={styles.statValue}>44.1k</Text>
            <Text style={styles.statLabel}>Sample Rate</Text>
          </View>
        </View>
      </View>

      {/* Stems List */}
      <View style={styles.stemsList}>
        {stems.map((stem) => (
          <StemCard
            key={stem.name}
            name={stem.name}
            duration={stem.duration}
            waveform={stem.waveform}
            color={stemColors[stem.name] || colors.accent}
            isPlaying={stem.isPlaying}
            onPlay={() => handlePlay(stem.name)}
            onDownload={() => handleDownload(stem.name)}
          />
        ))}
      </View>

      {/* Export All */}
      <TouchableOpacity
        style={styles.exportButton}
        onPress={handleExportAll}
        disabled={isExporting}
      >
        {isExporting ? (
          <ActivityIndicator color={colors.background} />
        ) : (
          <Text style={styles.exportText}>Export All Stems</Text>
        )}
      </TouchableOpacity>

      {/* Format Options */}
      <View style={styles.formatSection}>
        <Text style={styles.formatLabel}>Export Format</Text>
        <View style={styles.formatOptions}>
          {['WAV', 'FLAC', 'MP3'].map((format) => (
            <TouchableOpacity
              key={format}
              style={[
                styles.formatButton,
                format === 'WAV' && styles.formatButtonActive,
              ]}
            >
              <Text
                style={[
                  styles.formatText,
                  format === 'WAV' && styles.formatTextActive,
                ]}
              >
                {format}
              </Text>
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
    ...typography.mono,
    color: colors.textSecondary,
    fontSize: 12,
  },
  provenanceCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  provenanceLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  provenanceHash: {
    ...typography.mono,
    color: colors.accent,
    marginBottom: spacing.md,
  },
  provenanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  provenanceStat: {
    alignItems: 'center',
  },
  statValue: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textMuted,
  },
  stemsList: {
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  exportButton: {
    backgroundColor: colors.accent,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  exportText: {
    ...typography.body,
    color: colors.background,
    fontWeight: '600',
  },
  formatSection: {
    marginBottom: spacing.xl,
  },
  formatLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  formatOptions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  formatButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  formatButtonActive: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  formatText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  formatTextActive: {
    color: colors.background,
    fontWeight: '600',
  },
});
