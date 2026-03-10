import React, { useState, useCallback, useRef } from 'react';
import {
  View,
  Text,
  Image,
  FlatList,
  Pressable,
  ActivityIndicator,
  StyleSheet,
  RefreshControl,
  ViewToken,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SectionCard } from '../components/SectionCard';
import { JobItem } from '../components/JobItem';
import { Badge } from '../components/Badge';
import { useStory } from '../hooks/useStory';
import { colors, spacing, radius, fonts, typeIcons } from '../theme';
import type { StorySection } from '../types';

interface StoryScreenProps {
  storyUid: string;
  onBack: () => void;
}

export function StoryScreen({ storyUid, onBack }: StoryScreenProps) {
  const { story, jobs, loading, error, refresh } = useStory(storyUid);
  const [visibleUids, setVisibleUids] = useState<Set<string>>(new Set());

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      setVisibleUids((prev) => {
        const next = new Set(prev);
        for (const item of viewableItems) {
          if (item.isViewable && item.item?.uid) {
            next.add(item.item.uid);
          }
        }
        return next;
      });
    },
  ).current;

  const viewabilityConfig = useRef({ viewAreaCoveragePercentThreshold: 10 }).current;

  if (loading) {
    return (
      <View style={styles.container}>
        <StatusBar style="light" />
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </View>
    );
  }

  if (error || !story) {
    return (
      <View style={styles.container}>
        <StatusBar style="light" />
        <View style={styles.center}>
          <Text style={styles.errorText}>{error || 'Story not found'}</Text>
          <Pressable style={styles.backBtn} onPress={onBack}>
            <Text style={styles.backBtnText}>← Go back</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const sections = story.sections.filter((s) => s.title && s.text);
  const activeJobs = jobs.filter(
    (j) => j.status !== 'failed',
  );

  const renderHeader = () => (
    <View>
      {/* Back button */}
      <Pressable style={styles.backBtn} onPress={onBack}>
        <Text style={styles.backBtnText}>← Stories</Text>
      </Pressable>

      {/* Story header */}
      <View style={styles.detailHeader}>
        {story.cover_image ? (
          <Image
            source={{ uri: story.cover_image }}
            style={styles.cover}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.coverPlaceholder}>
            <Text style={styles.coverIcon}>
              {typeIcons[story.story_type] || '📝'}
            </Text>
          </View>
        )}
        <View style={styles.detailInfo}>
          <Text style={styles.detailTitle}>{story.title}</Text>
          {story.author ? (
            <Text style={styles.detailAuthor}>by {story.author}</Text>
          ) : null}
          {story.description ? (
            <Text style={styles.detailDesc} numberOfLines={3}>
              {story.description}
            </Text>
          ) : null}
          <View style={styles.badgeRow}>
            <Badge type={story.story_type} />
          </View>
        </View>
      </View>

      {/* Jobs section */}
      {activeJobs.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Generation Jobs</Text>
          <View style={styles.jobsList}>
            {activeJobs.map((job) => (
              <JobItem key={job.uid} job={job} />
            ))}
          </View>
        </View>
      ) : null}

      {/* Section header */}
      <View style={styles.sectionHeaderRow}>
        <Text style={styles.sectionTitle}>Story Cards</Text>
        <Text style={styles.sectionCount}>
          {sections.length} card{sections.length !== 1 ? 's' : ''}
        </Text>
      </View>
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.empty}>
      <Text style={styles.emptyIcon}>🎴</Text>
      <Text style={styles.emptyText}>
        No cards generated yet.{'\n'}Trigger generation via the CLI.
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <FlatList<StorySection>
        data={sections}
        keyExtractor={(item) => item.uid}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={styles.listContent}
        ItemSeparatorComponent={() => <View style={styles.cardSeparator} />}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        refreshControl={
          <RefreshControl
            refreshing={false}
            onRefresh={refresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
            progressBackgroundColor={colors.card}
          />
        }
        renderItem={({ item }) => (
          <View style={styles.cardWrapper}>
            <SectionCard
              section={item}
              isVisible={visibleUids.has(item.uid)}
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xxl,
  },
  errorText: {
    fontSize: 14,
    color: colors.red,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  listContent: {
    paddingTop: 56,
    paddingHorizontal: spacing.xxl,
    paddingBottom: 40,
  },
  backBtn: {
    alignSelf: 'flex-start',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    marginBottom: spacing.lg,
  },
  backBtnText: {
    fontSize: 14,
    color: colors.textSecondary,
    ...fonts.medium,
  },
  detailHeader: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginBottom: spacing.xl,
  },
  cover: {
    width: 100,
    height: 145,
    borderRadius: radius.lg,
    backgroundColor: colors.card,
  },
  coverPlaceholder: {
    width: 100,
    height: 145,
    borderRadius: radius.lg,
    backgroundColor: colors.card,
    alignItems: 'center',
    justifyContent: 'center',
  },
  coverIcon: {
    fontSize: 36,
  },
  detailInfo: {
    flex: 1,
    gap: spacing.xs,
  },
  detailTitle: {
    fontSize: 20,
    color: colors.white,
    ...fonts.bold,
  },
  detailAuthor: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  detailDesc: {
    fontSize: 13,
    color: colors.textMuted,
    lineHeight: 19,
  },
  badgeRow: {
    flexDirection: 'row',
    marginTop: spacing.xs,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: 12,
    color: colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
    marginBottom: spacing.md,
    ...fonts.semibold,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionCount: {
    fontSize: 12,
    color: colors.textDim,
  },
  jobsList: {
    gap: spacing.sm,
  },
  cardWrapper: {
    alignItems: 'center',
  },
  cardSeparator: {
    height: spacing.lg,
  },
  empty: {
    alignItems: 'center',
    paddingTop: 48,
  },
  emptyIcon: {
    fontSize: 36,
    marginBottom: spacing.md,
  },
  emptyText: {
    fontSize: 14,
    color: colors.textDim,
    textAlign: 'center',
    lineHeight: 22,
  },
});
