<!-- src/components/NovelCard.vue -->
<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 group">
    <router-link :to="`/novel/${novel.id}`" class="block">
      <!-- 封面圖片區 -->
      <div class="relative h-48 bg-gray-200 dark:bg-gray-700">
        <img 
          v-if="novel.cover_image" 
          :src="novel.cover_image" 
          :alt="novel.title" 
          class="w-full h-full object-cover"
        >
        <!-- 預設封面 -->
        <div v-else class="w-full h-full flex items-center justify-center">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
        </div>
        <!-- 小說狀態標籤 -->
        <span class="absolute top-2 right-2 text-xs font-semibold px-2 py-1 rounded-full" :class="statusInfo.class">
          {{ statusInfo.text }}
        </span>
      </div>

      <!-- 文字資訊區 -->
      <div class="p-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white truncate group-hover:text-blue-500 transition-colors">
          {{ novel.title }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          作者：<router-link 
            :to="{ name: 'Author', params: { id: novel.author.user_id } }" 
            @click.stop
            class="hover:underline hover:text-blue-500"
          >
            {{ novel.author.pen_name || novel.author.username }}
          </router-link>
        </p>
        <p class="text-sm text-gray-700 dark:text-gray-300 mt-2 h-10 overflow-hidden text-ellipsis">
          {{ novel.description }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-3 text-right">
          最後更新：{{ formattedDate }}
        </p>
      </div>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'; // 值導入
import type { PropType } from 'vue'; // 類型導入
import type { Novel } from '../types'; // 類型導入

const props = defineProps({
  novel: {
    type: Object as PropType<Novel>,
    required: true,
  },
});

// 格式化日期
const formattedDate = computed(() => {
  return new Date(props.novel.updated_at).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});

// 轉換狀態文字和樣式
const statusInfo = computed(() => {
  switch (props.novel.status) {
    case 'ONGOING':
      return { text: '連載中', class: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' };
    case 'COMPLETED':
      return { text: '已完結', class: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' };
    case 'HIATUS':
      return { text: '休刊中', class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' };
    default:
      return { text: '未知', class: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' };
  }
});
</script>