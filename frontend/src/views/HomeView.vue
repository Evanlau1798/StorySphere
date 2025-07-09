<!-- src/views/HomeView.vue -->
<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8">
    <!-- 歡迎橫幅 -->
    <div class="text-center py-10 sm:py-16">
      <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-4">
        探索精彩的故事世界
      </h1>
      <p class="text-base md:text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
        在這裡，每一個故事都值得被發現。開始您的閱讀之旅，或分享您的創作。
      </p>
    </div>

    <!-- 小說列表區 -->
    <div class="mt-8">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">最新更新</h2>
      
      <!-- 載入中狀態 -->
      <div v-if="isLoading" class="text-center py-10">
        <p class="text-gray-500 dark:text-gray-400">正在載入小說...</p>
        <!-- 可以放一個 Loading Spinner -->
      </div>
      
      <!-- 錯誤狀態 -->
      <div v-else-if="error" class="text-center py-10 bg-red-100 dark:bg-red-900/20 p-4 rounded-lg">
        <p class="text-red-600 dark:text-red-400 font-semibold">載入失敗</p>
        <p class="text-red-500 dark:text-red-500 mt-2">{{ error }}</p>
        <button @click="fetchNovels" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">重試</button>
      </div>

      <!-- 成功載入數據 -->
      <div v-else-if="novels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <NovelCard v-for="novel in novels" :key="novel.id" :novel="novel" />
      </div>

      <!-- 沒有數據狀態 -->
      <div v-else class="text-center py-10">
        <p class="text-gray-500 dark:text-gray-400">目前還沒有任何小說。</p>
      </div>
    </div>

    <!-- TODO: 分頁控制項將會加在這裡 -->

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../api/axios';
import type { Novel, PaginatedResponse } from '../types';
import NovelCard from '../components/NovelCard.vue';

const novels = ref<Novel[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

const fetchNovels = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<PaginatedResponse<Novel>>('/novels/');
    novels.value = response.data.results;
  } catch (err: any) {
    console.error("Failed to fetch novels:", err);
    error.value = err.message || "無法從伺服器獲取資料。";
  } finally {
    isLoading.value = false;
  }
};

// 組件掛載後立即獲取數據
onMounted(() => {
  fetchNovels();
});
</script>