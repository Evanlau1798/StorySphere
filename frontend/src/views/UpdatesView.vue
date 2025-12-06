<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-white">最近更新</h1>

    <div v-if="isLoading" class="text-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">分類</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">書名</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hidden sm:table-cell">最新章節</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">作者</th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">更新時間</th>
                </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="novel in novels" :key="novel.id" class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                            {{ getCategoryLabel(novel.category) }}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <router-link :to="`/novel/${novel.id}`" class="text-sm font-medium text-gray-900 dark:text-white hover:text-blue-600">
                            {{ novel.title }}
                        </router-link>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                        {{ novel.latest_chapter || '暫無章節' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {{ novel.author.pen_name || novel.author.username }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                       {{ formatDate(novel.updated_at) }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../api/axios';
import type { Novel } from '../types';

const novels = ref<Novel[]>([]);
const isLoading = ref(true);

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    'FANTASY': '奇幻', 'SCIFI': '科幻', 'ROMANCE': '言情',
    'URBAN': '都市', 'HISTORY': '歷史', 'MARTIAL': '武俠',
    'YURI': '百合', 'OTHERS': '其他'
  };
  return map[category] || '其他';
};

const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.round(diffMs / 60000);
    const diffHrs = Math.round(diffMs / 3600000);

    if (diffMins < 60) return `${diffMins} 分鐘前`;
    if (diffHrs < 24) return `${diffHrs} 小時前`;
    return date.toLocaleDateString();
};

const fetchUpdates = async () => {
    try {
        const response = await apiClient.get<Novel[]>('/novels/', {
            params: { ordering: '-updated_at' }
        });
        const results = Array.isArray(response.data) ? response.data : (response.data as any).results;
        novels.value = results;
    } catch (error) {
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchUpdates);
</script>