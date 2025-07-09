<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-white">我的書架</h1>

    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <NovelCardSkeleton v-for="n in 8" :key="n" />
    </div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>
    <div v-else-if="bookshelf.length === 0" class="text-center py-10 text-gray-500">
      書架是空的，快去探索喜歡的小說吧！
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <NovelCard v-for="item in bookshelf" :key="item.id" :novel="item">
        <template #footer>
          <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            <p>最後閱讀：{{ formatTimestamp(item.lastReadTimestamp) }}</p>
            <p>進度：{{ item.lastReadChapterTitle }} - 第 {{ item.lastReadPage }} 頁</p>
          </div>
        </template>
      </NovelCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../api/axios';
import type { Novel } from '../types';
import NovelCard from '../components/NovelCard.vue';
import NovelCardSkeleton from '../components/NovelCardSkeleton.vue';
import { useReadingProgressStore } from '../store/readingProgress';

interface BookshelfNovel extends Novel {
  lastReadTimestamp: number;
  lastReadChapterId: string;
  lastReadChapterTitle: string;
  lastReadPage: number;
}

const bookshelf = ref<BookshelfNovel[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const readingProgressStore = useReadingProgressStore();

const fetchBookshelf = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // Get all reading progress entries from the store
    const progressEntries = readingProgressStore.getRecentReadingProgress;

    if (progressEntries.length === 0) {
      bookshelf.value = [];
      return;
    }

    // Fetch novel details for each unique novel ID
    const uniqueNovelIds = [...new Set(progressEntries.map(p => p.novelId))];
    const fetchedNovels: { [key: string]: Novel } = {};
    for (const novelId of uniqueNovelIds) {
      try {
        const response = await apiClient.get<Novel>(`/novels/${novelId}/`);
        fetchedNovels[novelId] = response.data;
      } catch (err) {
        console.error(`Failed to fetch novel ${novelId}:`, err);
        // Optionally, remove this novel from recent progress if it's not found
      }
    }

    // Combine novel details with reading progress
    bookshelf.value = progressEntries
      .map(progress => {
        const novel = fetchedNovels[progress.novelId];
        if (!novel) return null;

        // --- CORRECTED CHAPTER FINDING LOGIC ---
        let chapterTitle = '未知章節';
        let foundChapter = null;

        // Search in volumes
        for (const volume of novel.volumes || []) {
          foundChapter = volume.chapters.find(c => c.id.toString() === progress.chapterId);
          if (foundChapter) break;
        }

        // If not found, search in chapters_without_volume
        if (!foundChapter && novel.chapters_without_volume) {
          foundChapter = novel.chapters_without_volume.find(c => c.id.toString() === progress.chapterId);
        }

        if (foundChapter) {
          chapterTitle = foundChapter.title;
        }
        // --- END OF CORRECTION ---

        return {
          ...novel,
          lastReadTimestamp: progress.timestamp,
          lastReadChapterId: progress.chapterId,
          lastReadChapterTitle: chapterTitle,
          lastReadPage: progress.page,
        };
      })
      .filter(Boolean) as BookshelfNovel[]; // Filter out nulls

  } catch (err) {
    error.value = '無法載入書架內容。';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

const formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp);
  return date.toLocaleString(); // Adjust format as needed
};

onMounted(fetchBookshelf);
</script>
