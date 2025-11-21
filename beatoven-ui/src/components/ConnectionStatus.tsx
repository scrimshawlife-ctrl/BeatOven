/**
 * ConnectionStatus - Backend connection indicator
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { colors, spacing, typography } from '../theme';
import { useBackend } from '../hooks/useBackend';

type Status = 'connected' | 'disconnected' | 'checking';

interface ConnectionStatusProps {
  showLabel?: boolean;
  onPress?: () => void;
}

export default function ConnectionStatus({
  showLabel = true,
  onPress,
}: ConnectionStatusProps) {
  const { checkHealth, backendUrl } = useBackend();
  const [status, setStatus] = useState<Status>('checking');
  const [version, setVersion] = useState<string | null>(null);
  const pulseAnim = React.useRef(new Animated.Value(1)).current;

  const checkConnection = useCallback(async () => {
    setStatus('checking');
    try {
      const result = await checkHealth();
      setStatus('connected');
      setVersion(result.version);
    } catch {
      setStatus('disconnected');
      setVersion(null);
    }
  }, [checkHealth]);

  // Check connection on mount and periodically
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [checkConnection, backendUrl]);

  // Pulse animation for checking state
  useEffect(() => {
    if (status === 'checking') {
      const animation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 0.4,
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
      animation.start();
      return () => animation.stop();
    } else {
      pulseAnim.setValue(1);
    }
  }, [status, pulseAnim]);

  const statusColors = {
    connected: colors.success,
    disconnected: colors.error,
    checking: colors.warning,
  };

  const statusLabels = {
    connected: version ? `v${version}` : 'Connected',
    disconnected: 'Offline',
    checking: 'Checking...',
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress || checkConnection}
      activeOpacity={0.7}
    >
      <Animated.View
        style={[
          styles.dot,
          {
            backgroundColor: statusColors[status],
            opacity: pulseAnim,
          },
        ]}
      />
      {showLabel && (
        <Text style={[styles.label, { color: statusColors[status] }]}>
          {statusLabels[status]}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  label: {
    ...typography.caption,
    fontSize: 11,
  },
});
