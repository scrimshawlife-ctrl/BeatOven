/**
 * Settings Screen - Backend URL, device mode, theme
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { colors, spacing, borderRadius, typography } from '../theme';
import { useBackend } from '../hooks/useBackend';

export default function SettingsScreen() {
  const { backendUrl, setBackendUrl, checkHealth } = useBackend();

  const [urlInput, setUrlInput] = useState(backendUrl);
  const [deviceMode, setDeviceMode] = useState<'local' | 'remote'>('local');
  const [isDarkTheme, setIsDarkTheme] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'connected' | 'error'>('unknown');
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    setUrlInput(backendUrl);
  }, [backendUrl]);

  const handleTestConnection = async () => {
    try {
      setConnectionStatus('unknown');
      const result = await checkHealth();
      setConnectionStatus('connected');
      setVersion(result.version);
    } catch (error) {
      setConnectionStatus('error');
      setVersion(null);
    }
  };

  const handleSaveUrl = async () => {
    await setBackendUrl(urlInput);
    handleTestConnection();
  };

  const handleResetDefaults = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to defaults?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            setUrlInput('http://localhost:8000');
            setDeviceMode('local');
            setIsDarkTheme(true);
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
        <Text style={styles.subtitle}>Configure BeatOven</Text>
      </View>

      {/* Backend URL */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Backend Configuration</Text>
        <View style={styles.card}>
          <Text style={styles.fieldLabel}>Backend URL</Text>
          <TextInput
            style={styles.input}
            value={urlInput}
            onChangeText={setUrlInput}
            placeholder="http://localhost:8000"
            placeholderTextColor={colors.textMuted}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
          />
          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.button} onPress={handleSaveUrl}>
              <Text style={styles.buttonText}>Save</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, styles.buttonSecondary]}
              onPress={handleTestConnection}
            >
              <Text style={[styles.buttonText, styles.buttonTextSecondary]}>
                Test Connection
              </Text>
            </TouchableOpacity>
          </View>

          {/* Connection Status */}
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Status:</Text>
            <View
              style={[
                styles.statusDot,
                connectionStatus === 'connected' && styles.statusConnected,
                connectionStatus === 'error' && styles.statusError,
              ]}
            />
            <Text style={styles.statusText}>
              {connectionStatus === 'unknown' && 'Unknown'}
              {connectionStatus === 'connected' && `Connected${version ? ` (v${version})` : ''}`}
              {connectionStatus === 'error' && 'Connection Failed'}
            </Text>
          </View>
        </View>
      </View>

      {/* Device Mode */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Device Mode</Text>
        <View style={styles.card}>
          <View style={styles.modeOptions}>
            {(['local', 'remote'] as const).map((mode) => (
              <TouchableOpacity
                key={mode}
                style={[
                  styles.modeButton,
                  deviceMode === mode && styles.modeButtonActive,
                ]}
                onPress={() => setDeviceMode(mode)}
              >
                <Text
                  style={[
                    styles.modeText,
                    deviceMode === mode && styles.modeTextActive,
                  ]}
                >
                  {mode === 'local' ? 'Local Backend' : 'Remote Server'}
                </Text>
                <Text style={styles.modeDesc}>
                  {mode === 'local'
                    ? 'Use local machine for generation'
                    : 'Use cloud GPU for generation'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* Theme */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>
        <View style={styles.card}>
          <View style={styles.toggleRow}>
            <View>
              <Text style={styles.toggleLabel}>Dark Theme</Text>
              <Text style={styles.toggleDesc}>
                Use dark colors (recommended)
              </Text>
            </View>
            <Switch
              value={isDarkTheme}
              onValueChange={setIsDarkTheme}
              trackColor={{ false: colors.surface, true: colors.accent }}
              thumbColor={isDarkTheme ? colors.background : colors.textMuted}
            />
          </View>
        </View>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.card}>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>App Version</Text>
            <Text style={styles.aboutValue}>1.0.0</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Engine</Text>
            <Text style={styles.aboutValue}>BeatOven Core</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Framework</Text>
            <Text style={styles.aboutValue}>ABX-Core v1.2</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Protocol</Text>
            <Text style={styles.aboutValue}>SEED Protocol</Text>
          </View>
        </View>
      </View>

      {/* Reset */}
      <TouchableOpacity
        style={styles.resetButton}
        onPress={handleResetDefaults}
      >
        <Text style={styles.resetText}>Reset to Defaults</Text>
      </TouchableOpacity>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          BeatOven - Generative Music Engine
        </Text>
        <Text style={styles.footerText}>
          Part of Applied Alchemy Labs
        </Text>
        <Text style={styles.footerLicense}>Apache 2.0 License</Text>
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
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  fieldLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  input: {
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.sm,
    padding: spacing.md,
    color: colors.textPrimary,
    ...typography.body,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  button: {
    flex: 1,
    backgroundColor: colors.accent,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    alignItems: 'center',
  },
  buttonSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonText: {
    ...typography.bodySmall,
    color: colors.background,
    fontWeight: '600',
  },
  buttonTextSecondary: {
    color: colors.textPrimary,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  statusLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.textMuted,
  },
  statusConnected: {
    backgroundColor: colors.success,
  },
  statusError: {
    backgroundColor: colors.error,
  },
  statusText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
  },
  modeOptions: {
    gap: spacing.sm,
  },
  modeButton: {
    backgroundColor: colors.surfaceLight,
    padding: spacing.md,
    borderRadius: borderRadius.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  modeButtonActive: {
    borderColor: colors.accent,
    backgroundColor: colors.surfaceLighter,
  },
  modeText: {
    ...typography.body,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  modeTextActive: {
    color: colors.accent,
  },
  modeDesc: {
    ...typography.caption,
    color: colors.textMuted,
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  toggleLabel: {
    ...typography.body,
    color: colors.textPrimary,
  },
  toggleDesc: {
    ...typography.caption,
    color: colors.textMuted,
  },
  aboutRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  aboutLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  aboutValue: {
    ...typography.bodySmall,
    color: colors.textPrimary,
  },
  resetButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.error,
    marginBottom: spacing.xl,
  },
  resetText: {
    ...typography.body,
    color: colors.error,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  footerText: {
    ...typography.caption,
    color: colors.textMuted,
  },
  footerLicense: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
});
