<!-- src/components/VolumeCard.vue -->
<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 group">
    <div class="block cursor-pointer">
      <!-- 封面圖片區 -->
      <div class="relative h-48 bg-gray-200 dark:bg-gray-700">
        <img 
          v-if="volume.cover_image" 
          :src="volume.cover_image" 
          :alt="volume.title" 
          class="w-full h-full object-cover"
        >
        <!-- 預設封面 -->
        <div v-else class="w-full h-full flex items-center justify-center">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
        </div>
      </div>

      <!-- 文字資訊區 -->
      <div class="p-3 flex flex-col flex-grow">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white truncate group-hover:text-blue-500 transition-colors text-center">
          {{ volume.title }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-2 flex-grow h-10 overflow-hidden text-ellipsis">
          {{ volume.description }}
        </p>
        <div class="text-xs text-gray-500 dark:text-gray-400 mt-3 pt-2 border-t border-gray-200 dark:border-gray-700 flex justify-between">
          <span>共 {{ volume.chapters.length }} 章</span>
          <span v-if="lastUpdatedDate">更新於 {{ lastUpdatedDate }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';
import type { Volume } from '../types';

const props = defineProps({
  volume: {
    type: Object as PropType<Volume>,
    required: true,
  },
});

const lastUpdatedDate = computed(() => {
  if (!props.volume.chapters || props.volume.chapters.length === 0) {
    return null;
  }
  // 找到最新的章節日期
  const latestChapter = props.volume.chapters.reduce((latest, chapter) => {
    const latestDate = new Date(latest.published_at);
    const chapterDate = new Date(chapter.published_at);
    return chapterDate > latestDate ? chapter : latest;
  });
  // 格式化日期
  return new Date(latestChapter.published_at).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
});
</script>