import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchStoryDetail, fetchStoryJobs } from '../api/stories';
import type { StoryDetail, GenerationJob } from '../types';

export function useStory(uid: string) {
  const [story, setStory] = useState<StoryDetail | null>(null);
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const [detail, jobList] = await Promise.all([
        fetchStoryDetail(uid),
        fetchStoryJobs(uid),
      ]);
      setStory(detail);
      setJobs(jobList);
      return jobList;
    } catch (e: any) {
      setError(e.message || 'Failed to load story');
      return [];
    } finally {
      setLoading(false);
    }
  }, [uid]);

  // Start polling if there are active jobs
  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      const jobList = await load();
      const hasActive = jobList.some(
        (j) => j.status === 'pending' || j.status === 'processing',
      );
      if (!hasActive && pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }, 3000);
  }, [load]);

  useEffect(() => {
    load().then((jobList) => {
      const hasActive = jobList.some(
        (j) => j.status === 'pending' || j.status === 'processing',
      );
      if (hasActive) startPolling();
    });

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [load, startPolling]);

  return { story, jobs, loading, error, refresh: load };
}
