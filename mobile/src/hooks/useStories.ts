import { useState, useEffect, useCallback } from 'react';
import { fetchStories } from '../api/stories';
import type { Story } from '../types';

export function useStories() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchStories();
      setStories(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load stories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { stories, loading, error, refresh: load };
}
