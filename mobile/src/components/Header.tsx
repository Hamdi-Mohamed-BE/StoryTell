import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { colors, spacing, fonts } from '../theme';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title = 'StoryCards', subtitle = 'AI-generated visual story cards' }: HeaderProps) {
  return (
    <View style={styles.header}>
      <StatusBar style="light" />
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingTop: 56,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.xxl,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.card,
  },
  title: {
    fontSize: 26,
    color: colors.primary,
    ...fonts.bold,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
});
