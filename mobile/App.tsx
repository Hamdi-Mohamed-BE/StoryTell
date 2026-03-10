import React, { useState } from 'react';
import { HomeScreen } from './src/screens/HomeScreen';
import { StoryScreen } from './src/screens/StoryScreen';

export default function App() {
  const [activeStoryUid, setActiveStoryUid] = useState<string | null>(null);

  if (activeStoryUid) {
    return (
      <StoryScreen
        storyUid={activeStoryUid}
        onBack={() => setActiveStoryUid(null)}
      />
    );
  }

  return <HomeScreen onSelectStory={setActiveStoryUid} />;
}
