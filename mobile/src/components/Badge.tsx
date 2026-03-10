import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, radius, fonts } from '../theme';

interface BadgeProps {
  type: string;
  icon?: string;
}

const icons: Record<string, string> = {
  book: '📖',
  movie: '🎬',
  anime: '🎌',
  show: '📺',
};

export function Badge({ type, icon }: BadgeProps) {
  const badgeColors = colors.badge[type] || { bg: colors.surface, text: colors.text };
  const emoji = icon || icons[type] || '📝';

  return (
    <View style={[styles.badge, { backgroundColor: badgeColors.bg }]}>
      <Text style={styles.icon}>{emoji}</Text>
      <Text style={[styles.label, { color: badgeColors.text }]}>{type}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.sm - 2,
  },
  icon: {
    fontSize: 11,
  },
  label: {
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    ...fonts.semibold,
  },
});
