import React from 'react';
import { View, Text, Image, Pressable, StyleSheet } from 'react-native';
import { colors, spacing, radius, fonts } from '../theme';
import { Badge } from './Badge';
import type { Story } from '../types';

interface StoryCardProps {
  story: Story;
  onPress: () => void;
}

const typeIcons: Record<string, string> = {
  book: '📖',
  movie: '🎬',
  anime: '🎌',
  show: '📺',
};

export function StoryCard({ story, onPress }: StoryCardProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      {story.cover_image ? (
        <Image
          source={{ uri: story.cover_image }}
          style={styles.cover}
          resizeMode="cover"
        />
      ) : (
        <View style={styles.coverPlaceholder}>
          <Text style={styles.coverIcon}>{typeIcons[story.story_type] || '📝'}</Text>
        </View>
      )}

      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={1}>
          {story.title}
        </Text>
        <View style={styles.meta}>
          <Badge type={story.story_type} />
          {story.author ? (
            <Text style={styles.author} numberOfLines={1}>
              by {story.author}
            </Text>
          ) : null}
        </View>
      </View>

      <Text style={styles.chevron}>›</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  cardPressed: {
    backgroundColor: colors.cardHover,
    borderColor: colors.primary,
  },
  cover: {
    width: 52,
    height: 72,
    borderRadius: radius.sm,
    backgroundColor: colors.card,
  },
  coverPlaceholder: {
    width: 52,
    height: 72,
    borderRadius: radius.sm,
    backgroundColor: colors.card,
    alignItems: 'center',
    justifyContent: 'center',
  },
  coverIcon: {
    fontSize: 24,
  },
  info: {
    flex: 1,
    gap: spacing.xs,
  },
  title: {
    fontSize: 15,
    color: colors.white,
    ...fonts.semibold,
  },
  meta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    flexWrap: 'wrap',
  },
  author: {
    fontSize: 12,
    color: colors.textMuted,
  },
  chevron: {
    fontSize: 22,
    color: colors.textDim,
    ...fonts.medium,
  },
});
