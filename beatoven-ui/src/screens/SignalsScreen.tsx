/**
 * Signals Screen - View and manage signal sources
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { colors, spacing, borderRadius, typography } from '../theme';
import { Skeleton, SkeletonList } from '../components/Skeleton';
import { useBackend } from '../hooks/useBackend';

interface SourceGroup {
  id: string;
  name: string;
  category: string;
  sources: string[];
  enabled: boolean;
  poll_interval_minutes: number;
}

interface SignalDocument {
  id: string;
  title: string;
  source_category: string;
  timestamp: string;
  symbolic_fields: {
    resonance: number;
    density: number;
    tension: number;
  };
}

export default function SignalsScreen() {
  const { apiCall, isLoading } = useBackend();
  const [groups, setGroups] = useState<SourceGroup[]>([]);
  const [recentSignals, setRecentSignals] = useState<SignalDocument[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const result = await apiCall<{ groups: SourceGroup[] }>('/signals/groups');
      setGroups(result.groups);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadGroups();
    setRefreshing(false);
  };

  const handleIngestGroup = async (groupId: string) => {
    // In production, would trigger group ingestion
    console.log(`Ingest group: ${groupId}`);
  };

  const renderGroupCard = (group: SourceGroup) => {
    const categoryColors: Record<string, string> = {
      world_news: colors.rhythm,
      us_news: colors.harmony,
      technology: colors.timbre,
      ai_ml: colors.motion,
      crypto_markets: colors.stems,
      music_industry: colors.accent,
    };

    const groupColor = categoryColors[group.category] || colors.textMuted;

    return (
      <View
        key={group.id}
        style={[styles.groupCard, { borderLeftColor: groupColor }]}
      >
        <View style={styles.groupHeader}>
          <Text style={styles.groupName}>{group.name}</Text>
          <View
            style={[
              styles.statusDot,
              { backgroundColor: group.enabled ? colors.success : colors.textMuted },
            ]}
          />
        </View>

        <Text style={styles.groupCategory}>{group.category.replace('_', ' ')}</Text>

        <Text style={styles.groupMeta}>
          {group.sources.length} sources • {group.poll_interval_minutes}min interval
        </Text>

        <TouchableOpacity
          style={styles.ingestButton}
          onPress={() => handleIngestGroup(group.id)}
        >
          <Text style={styles.ingestText}>Ingest Now</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={handleRefresh}
          tintColor={colors.accent}
        />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Signals</Text>
        <Text style={styles.subtitle}>
          Multi-source signal intake and normalization
        </Text>
      </View>

      {/* Source Groups */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Source Groups</Text>
        {isLoading ? (
          <SkeletonList count={3} />
        ) : groups.length === 0 ? (
          <Text style={styles.emptyText}>No source groups configured</Text>
        ) : (
          groups.map(renderGroupCard)
        )}
      </View>

      {/* Recent Signals */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Signals</Text>
        {recentSignals.length === 0 ? (
          <Text style={styles.emptyText}>No recent signals</Text>
        ) : (
          recentSignals.map((signal) => (
            <View key={signal.id} style={styles.signalCard}>
              <Text style={styles.signalTitle} numberOfLines={2}>
                {signal.title}
              </Text>
              <View style={styles.signalMeta}>
                <Text style={styles.signalField}>
                  R:{signal.symbolic_fields.resonance.toFixed(2)}
                </Text>
                <Text style={styles.signalField}>
                  D:{signal.symbolic_fields.density.toFixed(2)}
                </Text>
                <Text style={styles.signalField}>
                  T:{signal.symbolic_fields.tension.toFixed(2)}
                </Text>
              </View>
            </View>
          ))
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
  groupCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderLeftWidth: 3,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  groupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  groupName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  groupCategory: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'capitalize',
    marginBottom: spacing.sm,
  },
  groupMeta: {
    ...typography.caption,
    color: colors.textMuted,
    marginBottom: spacing.md,
  },
  ingestButton: {
    backgroundColor: colors.surfaceLight,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
    alignSelf: 'flex-start',
  },
  ingestText: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: '500',
  },
  signalCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  signalTitle: {
    ...typography.body,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  signalMeta: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  signalField: {
    ...typography.mono,
    color: colors.accent,
    fontSize: 11,
  },
  emptyText: {
    ...typography.body,
    color: colors.textMuted,
    textAlign: 'center',
    padding: spacing.lg,
  },
});
