import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL_KEY = 'storycards_api_url';
const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000';

let cachedUrl: string | null = null;

export async function getApiUrl(): Promise<string> {
  if (cachedUrl) return cachedUrl;
  const stored = await AsyncStorage.getItem(API_URL_KEY);
  cachedUrl = stored || DEFAULT_API_URL;
  return cachedUrl;
}

/** Sync getter — returns cached URL or the default. Safe to call after any apiFetch. */
export function getApiUrlSync(): string {
  return cachedUrl || DEFAULT_API_URL;
}

export async function setApiUrl(url: string): Promise<void> {
  cachedUrl = url;
  await AsyncStorage.setItem(API_URL_KEY, url);
}

export async function apiFetch<T>(path: string): Promise<T> {
  const base = await getApiUrl();
  const url = `${base}${path}`;
  console.log(`[apiFetch] GET ${url}`);
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error(`[apiFetch] ${res.status} ${url}`, err);
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  console.log(`[apiFetch] ${res.status} OK ${url}`);
  return res.json();
}
