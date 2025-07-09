import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface ReadingProgress {
  novelId: string;
  chapterId: string;
  page: number;
  timestamp: number;
}

export const useReadingProgressStore = defineStore('readingProgress', () => {
  // Map to store reading progress for each novel: novelId -> ReadingProgress
  const allReadingProgress = ref<Map<string, ReadingProgress>>(new Map());

  // Load all reading progress from localStorage on store initialization
  const loadAllReadingProgress = () => {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('readingProgress_')) {
        try {
          const progress = JSON.parse(localStorage.getItem(key) as string) as ReadingProgress;
          allReadingProgress.value.set(progress.novelId, progress);
        } catch (e) {
          console.error('Error parsing reading progress from localStorage', e);
          localStorage.removeItem(key); // Remove corrupted data
        }
      }
    });
  };

  // Save a specific novel's reading progress
  const saveReadingProgress = (progress: ReadingProgress) => {
    // Update the progress for the novel
    allReadingProgress.value.set(progress.novelId, progress);

    // Sort by timestamp to find the oldest entry if we exceed the limit
    const sortedProgress = Array.from(allReadingProgress.value.values()).sort((a, b) => a.timestamp - b.timestamp);

    // If we have more than 10 entries, remove the oldest one
    if (sortedProgress.length > 10) {
      const oldestProgress = sortedProgress[0];
      allReadingProgress.value.delete(oldestProgress.novelId);
      localStorage.removeItem(`readingProgress_${oldestProgress.novelId}`);
    }

    // Save the current progress to localStorage
    localStorage.setItem(`readingProgress_${progress.novelId}`, JSON.stringify(progress));
  };

  // Get reading progress for a specific novel
  const getReadingProgress = (novelId: string) => {
    return allReadingProgress.value.get(novelId);
  };

  // Get all reading progress entries, sorted by timestamp (most recent first)
  const getRecentReadingProgress = computed(() => {
    return Array.from(allReadingProgress.value.values()).sort((a, b) => b.timestamp - a.timestamp);
  });

  // Initialize when the store is created
  loadAllReadingProgress();

  return {
    allReadingProgress,
    saveReadingProgress,
    getReadingProgress,
    getRecentReadingProgress,
  };
});
