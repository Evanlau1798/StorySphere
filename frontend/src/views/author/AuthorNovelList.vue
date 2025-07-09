<!-- src/views/author/AuthorNovelList.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white">我的小說</h1>
      <router-link to="/dashboard/novels/new" class="bg-blue-500 text-white px-6 py-2 rounded-lg shadow hover:bg-blue-600 transition-colors">
        新增小說
      </router-link>
    </div>

    <div v-if="isLoading" class="text-center text-gray-500 dark:text-gray-400">載入中...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>

    <div v-else-if="novels.length === 0" class="text-center text-gray-500 dark:text-gray-400">
      <p>您尚未建立任何小說。</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div 
        v-for="novel in novels" 
        :key="novel.id" 
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 group relative"
      >
        <div @click="navigateToNovelEdit(novel.id)" class="cursor-pointer">
          <img :src="novel.cover_image || '/placeholder.jpg'" alt="Novel Cover" class="w-full h-48 object-cover">
          <div class="p-4">
            <h2 class="text-xl font-bold truncate text-gray-800 dark:text-white" :title="novel.title">{{ novel.title }}</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ novel.author_name }}</p>
            <div class="mt-2 text-sm text-gray-500 dark:text-gray-300">
              <span>{{ novel.status }}</span>
              <span class="mx-2">•</span>
              <span>最後更新: {{ new Date(novel.updated_at).toLocaleDateString() }}</span>
            </div>
          </div>
        </div>
        <button @click.stop="deleteNovel(novel.id)" class="absolute top-2 right-2 bg-red-500 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../api/axios';
import type { Novel } from '../../types';
import { eventBus, EventType } from '../../composables/useEventBus';

const novels = ref<Novel[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const router = useRouter();

const fetchNovels = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/novels/?my_novels=true');
    novels.value = response.data.results;
  } catch (err) {
    console.error(err);
    error.value = '無法載入小說列表。';
  } finally {
    isLoading.value = false;
  }
};

const navigateToNovelEdit = (novelId: number) => {
  router.push(`/dashboard/novels/${novelId}/edit`);
};

const deleteNovel = async (novelId: number) => {
  if (window.confirm('您確定要刪除這本小說嗎？此操作無法復原。')) {
    try {
      await apiClient.delete(`/novels/${novelId}/`);
      novels.value = novels.value.filter(n => n.id !== novelId);
      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '小說已刪除。',
      });
    } catch (err) {
      console.error('Failed to delete novel', err);
      eventBus.emit(EventType.ShowAlert, {
        type: 'error',
        title: '錯誤',
        message: '刪除失敗，請稍後再試。',
      });
    }
  }
};

onMounted(fetchNovels);
</script>
