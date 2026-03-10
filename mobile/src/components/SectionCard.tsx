import React, { useState, useEffect, useRef } from 'react';
import { View, Text, Image, StyleSheet, Dimensions, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Audio } from 'expo-av';
import { colors, spacing, radius, fonts } from '../theme';
import { fetchSectionMedia } from '../api/stories';
import { getApiUrlSync } from '../api/client';
import type { StorySection, SectionMedia } from '../types';

interface SectionCardProps {
  section: StorySection;
  isVisible: boolean;
}

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const CARD_WIDTH = SCREEN_WIDTH - spacing.xxl * 2;
const IMAGE_HEIGHT = 240;

/** Turn a relative /media/... path into a full URL. Already-absolute URLs pass through. */
function resolveUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('http') || url.startsWith('data:')) return url;
  return `${getApiUrlSync()}${url}`;
}

export function SectionCard({ section, isVisible }: SectionCardProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loadingMedia, setLoadingMedia] = useState(false);
  const fetchedRef = useRef(false);

  // Audio player state
  const soundRef = useRef<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [progress, setProgress] = useState(0); // 0-1

  // Cleanup sound on unmount
  useEffect(() => {
    return () => {
      soundRef.current?.unloadAsync();
    };
  }, []);

  const toggleAudio = async () => {
    if (!audioUrl) return;

    try {
      // Already loaded — toggle play/pause
      if (soundRef.current) {
        const status = await soundRef.current.getStatusAsync();
        if (status.isLoaded && status.isPlaying) {
          await soundRef.current.pauseAsync();
          setIsPlaying(false);
          console.log(`⏸️ [Audio] section[${section.section_index}] paused`);
        } else {
          await soundRef.current.playAsync();
          setIsPlaying(true);
          console.log(`▶️ [Audio] section[${section.section_index}] playing`);
        }
        return;
      }

      // First tap — load and play
      setAudioLoading(true);
      console.log(`🔊 [Audio] section[${section.section_index}] loading: ${audioUrl}`);
      const { sound } = await Audio.Sound.createAsync(
        { uri: audioUrl },
        { shouldPlay: true },
        (status) => {
          if (!status.isLoaded) return;
          setIsPlaying(status.isPlaying);
          if (status.durationMillis && status.durationMillis > 0) {
            setProgress(status.positionMillis / status.durationMillis);
          }
          if (status.didJustFinish) {
            setIsPlaying(false);
            setProgress(0);
            soundRef.current?.setPositionAsync(0);
          }
        },
      );
      soundRef.current = sound;
      setIsPlaying(true);
      setAudioLoading(false);
      console.log(`✅ [Audio] section[${section.section_index}] loaded and playing`);
    } catch (err) {
      console.error(`❌ [Audio] section[${section.section_index}] error:`, err);
      setAudioLoading(false);
    }
  };

  useEffect(() => {
    console.log(
      `[SectionCard] section[${section.section_index}] visible=${isVisible} has_image=${section.has_image} has_audio=${section.has_audio} imageUrl=${imageUrl} loading=${loadingMedia}`,
    );

    // Already fetched or currently fetching — skip
    if (fetchedRef.current || loadingMedia) return;
    if (!isVisible) return;
    if (!section.has_image && !section.has_audio) {
      console.log(`[SectionCard] section[${section.section_index}] skipped — no media flags`);
      return;
    }

    fetchedRef.current = true;
    setLoadingMedia(true);
    console.log(`[SectionCard] section[${section.section_index}] fetching media for uid=${section.uid}`);
    fetchSectionMedia(section.uid)
      .then((data) => {
        const resolvedImage = resolveUrl(data.image_url);
        const resolvedAudio = resolveUrl(data.audio_url);

        console.log(
          `\u2705 [SectionCard] section[${section.section_index}] FINAL image URL:`,
          resolvedImage,
        );
        console.log(
          `\u2705 [SectionCard] section[${section.section_index}] FINAL audio URL:`,
          resolvedAudio,
        );

        setImageUrl(resolvedImage);
        setAudioUrl(resolvedAudio);
      })
      .catch((err) => {
        console.error(`\u274C [SectionCard] section[${section.section_index}] media fetch error:`, err);
        fetchedRef.current = false; // Allow retry on error
      })
      .finally(() => {
        setLoadingMedia(false);
      });
  }, [isVisible, section.uid, section.has_image, section.has_audio]);

  return (
    <View style={styles.card}>
      {loadingMedia && section.has_image ? (
        <View style={styles.imagePlaceholder}>
          <ActivityIndicator size="small" color={colors.primary} />
        </View>
      ) : imageUrl ? (
        <Image
          source={{ uri: imageUrl }}
          style={styles.image}
          resizeMode="cover"
          onLoad={() => console.log(`\u2705 [Image] section[${section.section_index}] loaded OK`)}
          onError={(e) => console.error(`\u274C [Image] section[${section.section_index}] error:`, e.nativeEvent.error, imageUrl)}
        />
      ) : section.has_image ? (
        <View style={styles.imagePlaceholder}>
          <Text style={styles.placeholderText}>Tap to load image</Text>
        </View>
      ) : (
        <View style={styles.imagePlaceholder}>
          <Text style={styles.placeholderText}>No image generated</Text>
        </View>
      )}

      <View style={styles.body}>
        <View style={styles.indexBadge}>
          <Text style={styles.indexText}>{section.section_index}</Text>
        </View>

        <Text style={styles.title}>{section.title}</Text>
        <Text style={styles.text}>{section.text}</Text>

        {section.image_prompt ? (
          <View style={styles.promptRow}>
            <Text style={styles.promptIcon}>🎨</Text>
            <Text style={styles.promptText} numberOfLines={2}>
              {section.image_prompt}
            </Text>
          </View>
        ) : null}

        {audioUrl ? (
          <TouchableOpacity style={styles.audioRow} onPress={toggleAudio} activeOpacity={0.7}>
            {audioLoading ? (
              <ActivityIndicator size="small" color={colors.primary} />
            ) : (
              <Text style={styles.audioIcon}>{isPlaying ? '⏸' : '▶️'}</Text>
            )}
            <View style={styles.progressTrack}>
              <View style={[styles.progressFill, { width: `${Math.round(progress * 100)}%` }]} />
            </View>
            <Text style={styles.audioLabel}>{isPlaying ? 'Playing' : 'Play narration'}</Text>
          </TouchableOpacity>
        ) : section.has_audio && !loadingMedia ? (
          <View style={styles.audioRow}>
            <Text style={styles.audioIcon}>🔇</Text>
            <Text style={styles.audioLabel}>Audio loading...</Text>
          </View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.border,
    width: CARD_WIDTH,
  },
  image: {
    width: '100%',
    height: IMAGE_HEIGHT,
    backgroundColor: colors.surface,
  },
  imagePlaceholder: {
    width: '100%',
    height: IMAGE_HEIGHT,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    fontSize: 14,
    color: colors.textDim,
  },
  body: {
    padding: spacing.xl,
  },
  indexBadge: {
    width: 28,
    height: 28,
    borderRadius: radius.sm,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  indexText: {
    fontSize: 13,
    color: colors.white,
    ...fonts.bold,
  },
  title: {
    fontSize: 17,
    color: colors.white,
    marginBottom: spacing.sm,
    ...fonts.semibold,
  },
  text: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  promptRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 6,
    marginTop: spacing.md,
  },
  promptIcon: {
    fontSize: 12,
    marginTop: 2,
  },
  promptText: {
    flex: 1,
    fontSize: 12,
    color: colors.textDim,
    fontStyle: 'italic',
  },
  audioRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginTop: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.sm,
  },
  audioIcon: {
    fontSize: 18,
    width: 28,
    textAlign: 'center',
  },
  progressTrack: {
    flex: 1,
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 2,
  },
  audioLabel: {
    fontSize: 12,
    color: colors.textDim,
  },
});
