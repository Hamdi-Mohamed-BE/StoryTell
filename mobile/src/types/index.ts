export interface Story {
  uid: string;
  title: string;
  description: string | null;
  story_type: string;
  author: string | null;
  cover_image: string | null;
  created_at: string;
}

export interface StorySection {
  uid: string;
  section_index: number;
  title: string;
  text: string;
  image_prompt: string | null;
  has_image: boolean;
  has_audio: boolean;
}

export interface SectionMedia {
  uid: string;
  section_index: number;
  title: string;
  text: string;
  image_prompt: string | null;
  image_url: string | null;
  audio_url: string | null;
}

export interface StoryDetail extends Story {
  sections: StorySection[];
}

export interface GenerationJob {
  uid: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_sections: number;
  generated_sections: number;
  error_message: string | null;
  created_at: string;
}
