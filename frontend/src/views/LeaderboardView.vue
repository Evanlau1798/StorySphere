<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8 text-center text-gray-800 dark:text-white">排行榜</h1>

    <div class="max-w-4xl mx-auto">
      <!-- Tabs -->
      <div class="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          @click="activeTab = 'popular'"
          :class="['px-6 py-3 font-medium transition-colors', activeTab === 'popular' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']"
        >
          人氣排行榜
        </button>
        <button 
          @click="activeTab = 'updated'"
          :class="['px-6 py-3 font-medium transition-colors', activeTab === 'updated' ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400']"
        >
          最新更新榜
        </button>
      </div>

      <!-- List -->
      <div v-if="isLoading" class="space-y-4">
        <div v-for="n in 5" :key="n" class="h-24 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"></div>
      </div>

      <div v-else class="space-y-4">
        <div v-for="(novel, index) in novels" :key="novel.id" class="flex items-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
          <!-- Rank Badge -->
          <div class="flex-shrink-0 w-12 text-center mr-4">
             <span 
              class="inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-white text-lg"
              :class="getRankClass(index)"
            >
              {{ index + 1 }}
            </span>
          </div>

          <!-- Cover -->
          <div class="flex-shrink-0 w-16 h-24 mr-4 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden">
            <img v-if="novel.cover_image" :src="novel.cover_image" :alt="novel.title" class="w-full h-full object-cover">
            <div v-else class="w-full h-full flex items-center justify-center">
               <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            </div>
          </div>

          <!-- Info -->
          <div class="flex-grow min-w-0">
            <router-link :to="`/novel/${novel.id}`">
              <h3 class="text-lg font-bold text-gray-800 dark:text-white hover:text-blue-600 truncate mb-1">
                {{ novel.title }}
              </h3>
            </router-link>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">
              {{ novel.author.pen_name || novel.author.username }}
            </p>
            <p class="text-xs text-gray-500 truncate">{{ novel.category }} | {{ novel.status === 'ONGOING' ? '連載中' : '已完結' }}</p>
          </div>

          <!-- Metadata -->
          <div class="flex-shrink-0 text-right ml-4">
            <div v-if="activeTab === 'popular'" class="text-blue-600 dark:text-blue-400 font-bold">
              {{ formatNumber(novel.views) }} 觀看
            </div>
            <div v-else class="text-gray-500 text-sm">
              {{ formatDate(novel.updated_at) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import apiClient from '../api/axios';
import type { Novel } from '../types';

const activeTab = ref<'popular' | 'updated'>('popular');
const novels = ref<Novel[]>([]);
const isLoading = ref(false);

const getRankClass = (index: number) => {
  if (index === 0) return 'bg-yellow-500'; // Gold
  if (index === 1) return 'bg-gray-400';   // Silver
  if (index === 2) return 'bg-orange-400'; // Bronze
  return 'bg-gray-300 dark:bg-gray-600 text-sm'; // Others
};

const formatNumber = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '萬';
  return num;
};

const formatDate = (dateString: string) => {
    // Return relative time if recent, else date
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
    if (diffDays <= 7) return `${diffDays} 天前`;
    return date.toLocaleDateString();
};

const fetchAndSort = async () => {
    isLoading.value = true;
    try {
        const ordering = activeTab.value === 'popular' ? '-views' : '-updated_at';
        const response = await apiClient.get<Novel[]>('/novels/', {
            params: {
                ordering: ordering,
                limit: 20 // Top 20
            }
        });
        // DRF Pagination handling if needed, assuming default response for now or small set
        // If ModelViewSet uses LimitOffsetPagination, response.data.results. 
        // Start simple assuming standard array or check structure.
        const results = Array.isArray(response.data) ? response.data : (response.data as any).results;
        novels.value = results; 
    } catch (e) {
        console.error(e);
    } finally {
        isLoading.value = false;
    }
}

watch(activeTab, () => {
    fetchAndSort();
});

onMounted(fetchAndSort);
</script>