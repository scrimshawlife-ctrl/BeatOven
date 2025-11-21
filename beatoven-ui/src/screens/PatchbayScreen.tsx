/**
 * PatchBay Screen - Visual node graph for modules
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, spacing, borderRadius, typography, shadows } from '../theme';
import NodeCard from '../components/NodeCard';
import type { RootStackParamList } from '../navigation';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

interface ModuleNode {
  id: string;
  name: string;
  type: 'rhythm' | 'harmony' | 'timbre' | 'motion' | 'stems' | 'runic';
  color: string;
  inputs: string[];
  outputs: string[];
  x: number;
  y: number;
}

const MODULES: ModuleNode[] = [
  {
    id: 'input',
    name: 'Input',
    type: 'rhythm',
    color: colors.textSecondary,
    inputs: [],
    outputs: ['symbolic'],
    x: 0,
    y: 0,
  },
  {
    id: 'rhythm',
    name: 'Rhythm',
    type: 'rhythm',
    color: colors.rhythm,
    inputs: ['symbolic'],
    outputs: ['events'],
    x: 1,
    y: 0,
  },
  {
    id: 'harmony',
    name: 'Harmony',
    type: 'harmony',
    color: colors.harmony,
    inputs: ['symbolic'],
    outputs: ['chords'],
    x: 1,
    y: 1,
  },
  {
    id: 'timbre',
    name: 'Timbre',
    type: 'timbre',
    color: colors.timbre,
    inputs: ['events', 'chords'],
    outputs: ['audio'],
    x: 2,
    y: 0,
  },
  {
    id: 'motion',
    name: 'Motion',
    type: 'motion',
    color: colors.motion,
    inputs: ['symbolic'],
    outputs: ['modulation'],
    x: 2,
    y: 1,
  },
  {
    id: 'stems',
    name: 'Stems',
    type: 'stems',
    color: colors.stems,
    inputs: ['audio', 'modulation'],
    outputs: ['wav'],
    x: 3,
    y: 0,
  },
  {
    id: 'runic',
    name: 'Runic',
    type: 'runic',
    color: colors.accent,
    inputs: ['symbolic', 'wav'],
    outputs: ['signature'],
    x: 3,
    y: 1,
  },
];

const CONNECTIONS: [string, string][] = [
  ['input', 'rhythm'],
  ['input', 'harmony'],
  ['input', 'motion'],
  ['rhythm', 'timbre'],
  ['harmony', 'timbre'],
  ['timbre', 'stems'],
  ['motion', 'stems'],
  ['input', 'runic'],
  ['stems', 'runic'],
];

export default function PatchbayScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [activeModule, setActiveModule] = useState<string | null>(null);

  const handleModulePress = (module: ModuleNode) => {
    setActiveModule(module.id);
    if (['rhythm', 'harmony', 'timbre', 'motion'].includes(module.type)) {
      navigation.navigate('Module', {
        moduleType: module.type as 'rhythm' | 'harmony' | 'timbre' | 'motion',
      });
    }
  };

  const renderConnection = (from: string, to: string, index: number) => {
    const fromNode = MODULES.find((m) => m.id === from);
    const toNode = MODULES.find((m) => m.id === to);
    if (!fromNode || !toNode) return null;

    return (
      <View
        key={`${from}-${to}-${index}`}
        style={[
          styles.connection,
          {
            left: (fromNode.x + 0.5) * 160,
            top: (fromNode.y + 0.5) * 120,
            width: Math.abs(toNode.x - fromNode.x) * 160,
            height: Math.abs(toNode.y - fromNode.y) * 120 || 2,
            transform: [
              { translateX: 0 },
              { rotate: toNode.y !== fromNode.y ? '45deg' : '0deg' },
            ],
          },
        ]}
      />
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Signal Flow</Text>
        <Text style={styles.subtitle}>Tap a module to configure</Text>
      </View>

      <View style={styles.graph}>
        {/* Connections */}
        <View style={styles.connectionsLayer}>
          {CONNECTIONS.map(([from, to], index) =>
            renderConnection(from, to, index)
          )}
        </View>

        {/* Nodes */}
        <View style={styles.nodesGrid}>
          {[0, 1, 2, 3].map((col) => (
            <View key={col} style={styles.column}>
              {MODULES.filter((m) => m.x === col).map((module) => (
                <NodeCard
                  key={module.id}
                  name={module.name}
                  color={module.color}
                  inputs={module.inputs}
                  outputs={module.outputs}
                  isActive={activeModule === module.id}
                  onPress={() => handleModulePress(module)}
                />
              ))}
            </View>
          ))}
        </View>
      </View>

      {/* Legend */}
      <View style={styles.legend}>
        <Text style={styles.legendTitle}>Modules</Text>
        <View style={styles.legendItems}>
          {[
            { name: 'Rhythm', color: colors.rhythm },
            { name: 'Harmony', color: colors.harmony },
            { name: 'Timbre', color: colors.timbre },
            { name: 'Motion', color: colors.motion },
            { name: 'Stems', color: colors.stems },
          ].map((item) => (
            <View key={item.name} style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: item.color }]} />
              <Text style={styles.legendText}>{item.name}</Text>
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
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  graph: {
    position: 'relative',
    minHeight: 300,
    marginBottom: spacing.xl,
  },
  connectionsLayer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 0,
  },
  connection: {
    position: 'absolute',
    backgroundColor: colors.border,
    height: 2,
  },
  nodesGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    zIndex: 1,
  },
  column: {
    flex: 1,
    gap: spacing.md,
  },
  legend: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  legendTitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  legendItems: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  legendText: {
    ...typography.caption,
    color: colors.textPrimary,
  },
});
