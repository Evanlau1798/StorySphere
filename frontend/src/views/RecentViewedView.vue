<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8 text-gray-800 dark:text-gray-200">最近瀏覽</h1>

    <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <NovelCardSkeleton v-for="n in 8" :key="n" />
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="recentNovels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <NovelCard 
        v-for="novel in recentNovels" 
        :key="novel.id"
        :novel="novel"
      >
        <template #footer>
          <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            <p>最後閱讀：{{ formatTimestamp(novel.lastReadTimestamp) }}</p>
            <p>進度：{{ novel.lastReadChapterTitle }} - 第 {{ novel.lastReadPage }} 頁</p>
          </div>
        </template>
      </NovelCard>
    </div>

    <div v-else class="text-center py-10 text-gray-500 dark:text-gray-400">
      <p>您還沒有瀏覽任何小說。</p>
      <router-link to="/explore" class="mt-4 inline-block px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        去探索小說
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useReadingProgressStore } from '@/store/readingProgress';
import apiClient from '@/api/axios';
import type { Novel } from '@/types';
import NovelCard from '@/components/NovelCard.vue';
import NovelCardSkeleton from '@/components/NovelCardSkeleton.vue'; // Assuming you have a skeleton loader

interface RecentNovel extends Novel {
  lastReadTimestamp: number;
  lastReadChapterId: string;
  lastReadChapterTitle: string;
  lastReadPage: number;
}

const readingProgressStore = useReadingProgressStore();
const isLoading = ref(true);
const error = ref<string | null>(null);
const recentNovels = ref<RecentNovel[]>([]);

const fetchRecentNovels = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const progressEntries = readingProgressStore.getRecentReadingProgress;
    const novelIds = progressEntries.map(p => p.novelId);

    if (novelIds.length === 0) {
      recentNovels.value = [];
      return;
    }

    // Fetch novel details for each unique novel ID
    const uniqueNovelIds = [...new Set(novelIds)];
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
    recentNovels.value = progressEntries
      .map(progress => {
        const novel = fetchedNovels[progress.novelId];
        if (!novel) return null;

        const chapter = novel.volumes.flatMap(v => v.chapters).find(c => c.id.toString() === progress.chapterId) ||
                        (novel.chapters_without_volume && novel.chapters_without_volume.find(c => c.id.toString() === progress.chapterId));
        const chapterTitle = chapter ? chapter.title : '未知章節';

        return {
          ...novel,
          lastReadTimestamp: progress.timestamp,
          lastReadChapterId: progress.chapterId,
          lastReadChapterTitle: chapterTitle,
          lastReadPage: progress.page,
        };
      })
      .filter(Boolean) as RecentNovel[]; // Filter out nulls

  } catch (err) {
    error.value = '無法載入最近瀏覽的小說。';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

const formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp);
  return date.toLocaleString(); // Adjust format as needed
};

onMounted(() => {
  fetchRecentNovels();
});

watch(() => readingProgressStore.allReadingProgress, () => {
  fetchRecentNovels();
}, { deep: true });
</script>
