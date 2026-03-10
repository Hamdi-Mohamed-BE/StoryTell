import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, radius, fonts } from '../theme';
import type { GenerationJob } from '../types';

interface JobBadgeProps {
  job: GenerationJob;
}

const statusColors: Record<string, { bg: string; text: string; border: string }> = {
  completed: { bg: colors.greenBg, text: colors.greenLight, border: colors.greenLight },
  processing: { bg: colors.blueBg, text: colors.blue, border: colors.blue },
  pending: { bg: colors.yellowBg, text: colors.yellow, border: colors.yellow },
  failed: { bg: colors.redBg, text: colors.red, border: colors.red },
};

export function JobItem({ job }: JobBadgeProps) {
  const sc = statusColors[job.status] || statusColors.pending;

  return (
    <View style={[styles.item, { borderLeftColor: sc.border }]}>
      <View>
        <View style={[styles.statusBadge, { backgroundColor: sc.bg }]}>
          <Text style={[styles.statusText, { color: sc.text }]}>{job.status}</Text>
        </View>
        {job.error_message ? (
          <Text style={styles.error} numberOfLines={1}>
            ⚠ {job.error_message}
          </Text>
        ) : null}
      </View>
      <View style={styles.metaRow}>
        <Text style={styles.meta}>
          {job.generated_sections}/{job.total_sections} sections
        </Text>
        {(job.status === 'processing' || job.status === 'pending') ? (
          <Text style={styles.spinner}>⟳</Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderLeftWidth: 3,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.sm - 2,
  },
  statusText: {
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    ...fonts.semibold,
  },
  error: {
    fontSize: 12,
    color: colors.red,
    marginTop: spacing.xs,
    maxWidth: 200,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  meta: {
    fontSize: 13,
    color: colors.textMuted,
  },
  spinner: {
    fontSize: 16,
    color: colors.primary,
  },
});
