import React from 'react';
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  Pressable,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { Header } from '../components/Header';
import { StoryCard } from '../components/StoryCard';
import { useStories } from '../hooks/useStories';
import { colors, spacing, fonts } from '../theme';

interface HomeScreenProps {
  onSelectStory: (uid: string) => void;
}

export function HomeScreen({ onSelectStory }: HomeScreenProps) {
  const { stories, loading, error, refresh } = useStories();

  return (
    <View style={styles.container}>
      <Header />

      {error ? (
        <View style={styles.center}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryBtn} onPress={refresh}>
            <Text style={styles.retryText}>Retry</Text>
          </Pressable>
        </View>
      ) : loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={stories}
          keyExtractor={(item) => item.uid}
          contentContainerStyle={styles.list}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshControl={
            <RefreshControl
              refreshing={loading}
              onRefresh={refresh}
              tintColor={colors.primary}
              colors={[colors.primary]}
              progressBackgroundColor={colors.card}
            />
          }
          renderItem={({ item }) => (
            <StoryCard
              story={item}
              onPress={() => onSelectStory(item.uid)}
            />
          )}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyIcon}>📚</Text>
              <Text style={styles.emptyText}>
                No stories yet.{'\n'}Add stories via the CLI or web panel.
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  list: {
    padding: spacing.lg,
    paddingBottom: 40,
  },
  separator: {
    height: spacing.sm,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xxl,
  },
  errorIcon: {
    fontSize: 32,
    marginBottom: spacing.md,
  },
  errorText: {
    fontSize: 14,
    color: colors.red,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  retryBtn: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: 10,
  },
  retryText: {
    color: colors.white,
    fontSize: 14,
    ...fonts.medium,
  },
  empty: {
    alignItems: 'center',
    paddingTop: 80,
  },
  emptyIcon: {
    fontSize: 40,
    marginBottom: spacing.md,
  },
  emptyText: {
    fontSize: 14,
    color: colors.textDim,
    textAlign: 'center',
    lineHeight: 22,
  },
});
