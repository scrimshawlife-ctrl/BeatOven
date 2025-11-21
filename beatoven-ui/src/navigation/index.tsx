/**
 * BeatOven Navigation
 */

import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet } from 'react-native';

import HomeScreen from '../screens/HomeScreen';
import PatchbayScreen from '../screens/PatchbayScreen';
import ModuleScreen from '../screens/ModuleScreen';
import StemsScreen from '../screens/StemsScreen';
import SymbolicPanelScreen from '../screens/SymbolicPanelScreen';
import SettingsScreen from '../screens/SettingsScreen';
import ConnectionStatus from '../components/ConnectionStatus';
import { colors } from '../theme';

export type RootStackParamList = {
  Main: undefined;
  Module: { moduleType: 'rhythm' | 'harmony' | 'timbre' | 'motion' };
  Stems: { jobId: string };
};

export type TabParamList = {
  Home: undefined;
  Patchbay: undefined;
  Symbolic: undefined;
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

// Tab icon component
function TabIcon({ name, focused }: { name: string; focused: boolean }) {
  const icons: Record<string, string> = {
    Home: '~',
    Patchbay: '#',
    Symbolic: '::',
    Settings: '=',
  };

  return (
    <View style={styles.iconContainer}>
      <Text style={[styles.icon, focused && styles.iconFocused]}>
        {icons[name] || '?'}
      </Text>
    </View>
  );
}

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused }) => (
          <TabIcon name={route.name} focused={focused} />
        ),
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabLabel,
        headerStyle: styles.header,
        headerTintColor: colors.textPrimary,
        headerTitleStyle: styles.headerTitle,
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          title: 'BeatOven',
          headerRight: () => <ConnectionStatus />,
        }}
      />
      <Tab.Screen
        name="Patchbay"
        component={PatchbayScreen}
        options={{ title: 'PatchBay' }}
      />
      <Tab.Screen
        name="Symbolic"
        component={SymbolicPanelScreen}
        options={{ title: 'Symbolic' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.background,
    card: colors.surface,
    text: colors.textPrimary,
    border: colors.border,
    primary: colors.accent,
  },
};

export default function Navigation() {
  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: styles.header,
          headerTintColor: colors.textPrimary,
          headerTitleStyle: styles.headerTitle,
        }}
      >
        <Stack.Screen
          name="Main"
          component={TabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="Module"
          component={ModuleScreen}
          options={({ route }) => ({
            title: route.params.moduleType.charAt(0).toUpperCase() +
              route.params.moduleType.slice(1),
          })}
        />
        <Stack.Screen
          name="Stems"
          component={StemsScreen}
          options={{ title: 'Stems' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.surface,
    borderTopColor: colors.border,
    borderTopWidth: 1,
    height: 60,
    paddingBottom: 8,
    paddingTop: 8,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '500',
  },
  header: {
    backgroundColor: colors.surface,
  },
  headerTitle: {
    fontWeight: '600',
    fontSize: 18,
  },
  iconContainer: {
    width: 28,
    height: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textMuted,
    fontFamily: 'monospace',
  },
  iconFocused: {
    color: colors.accent,
  },
});
