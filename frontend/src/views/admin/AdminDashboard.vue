<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">系統概覽</h1>

    <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Stats Cards -->
      <div class="bg-blue-50 dark:bg-blue-900/30 p-6 rounded-lg">
        <h3 class="text-blue-600 dark:text-blue-400 font-medium mb-2">總使用者數</h3>
        <p class="text-3xl font-bold text-gray-800 dark:text-white">{{ stats.user_count }}</p>
      </div>

      <div class="bg-green-50 dark:bg-green-900/30 p-6 rounded-lg">
        <h3 class="text-green-600 dark:text-green-400 font-medium mb-2">總小說數</h3>
        <p class="text-3xl font-bold text-gray-800 dark:text-white">{{ stats.novel_count }}</p>
      </div>

      <div class="bg-purple-50 dark:bg-purple-900/30 p-6 rounded-lg">
        <h3 class="text-purple-600 dark:text-purple-400 font-medium mb-2">總章節數</h3>
        <p class="text-3xl font-bold text-gray-800 dark:text-white">{{ stats.chapter_count }}</p>
      </div>

      <div class="bg-orange-50 dark:bg-orange-900/30 p-6 rounded-lg">
        <h3 class="text-orange-600 dark:text-orange-400 font-medium mb-2">全站總閱讀量</h3>
        <p class="text-3xl font-bold text-gray-800 dark:text-white">{{ stats.total_views }}</p>
      </div>
      
       <div class="col-span-1 md:col-span-2 lg:col-span-4 bg-gray-50 dark:bg-gray-700/50 p-6 rounded-lg mt-4">
        <h3 class="text-gray-600 dark:text-gray-300 font-medium mb-2">伺服器負載 (Server Load - 1/5/15 min)</h3>
        <p class="text-xl font-mono text-gray-800 dark:text-white">{{ stats.server_load.join(' / ') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api/axios'; // Make sure this path is correct or use alias
import { eventBus, EventType } from '../../composables/useEventBus';

const stats = ref({
  user_count: 0,
  novel_count: 0,
  chapter_count: 0,
  total_views: 0,
  server_load: [0, 0, 0]
});

const loading = ref(true);

onMounted(async () => {
    try {
        const response = await api.get('admin/stats/');
        stats.value = response.data;
    } catch (error) {
        console.error('Failed to fetch stats', error);
         eventBus.emit(EventType.ShowAlert, {
            type: 'error',
            title: '載入失敗',
            message: '無法獲取系統數據。',
        });
    } finally {
        loading.value = false;
    }
});
</script>
