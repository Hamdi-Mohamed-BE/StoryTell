import { apiFetch } from './client';
import type { Story, StoryDetail, StorySection, SectionMedia, GenerationJob } from '../types';

const API = '/api/stories';

export async function fetchStories(): Promise<Story[]> {
  return apiFetch<Story[]>(API);
}

export async function fetchStoryDetail(uid: string): Promise<StoryDetail> {
  return apiFetch<StoryDetail>(`${API}/${uid}`);
}

export async function fetchSectionMedia(sectionUid: string): Promise<SectionMedia> {
  return apiFetch<SectionMedia>(`${API}/sections/${sectionUid}/media`);
}

export async function fetchStorySections(uid: string): Promise<StorySection[]> {
  return apiFetch<StorySection[]>(`${API}/${uid}/sections`);
}

export async function fetchStoryJobs(uid: string): Promise<GenerationJob[]> {
  return apiFetch<GenerationJob[]>(`${API}/${uid}/jobs`);
}
