<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-white">探索小說</h1>
      
      <!-- Search and Filter Bar -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <!-- Search -->
        <div class="relative flex-grow">
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="搜尋小說或作者..." 
            class="w-full pl-10 pr-4 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <!-- Filters -->
        <div class="flex gap-2 overflow-x-auto pb-2 md:pb-0">
          <select v-model="selectedCategory" @change="fetchNovels" class="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="ALL">所有分類</option>
            <option value="FANTASY">奇幻</option>
            <option value="SCIFI">科幻</option>
            <option value="ROMANCE">言情</option>
            <option value="URBAN">都市</option>
            <option value="HISTORY">歷史</option>
            <option value="MARTIAL">武俠</option>
            <option value="OTHERS">其他</option>
          </select>

          <select v-model="selectedStatus" @change="fetchNovels" class="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="ALL">所有狀態</option>
            <option value="ONGOING">連載中</option>
            <option value="COMPLETED">已完結</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Novel Grid -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
    </div>
    
    <div v-else-if="novels.length === 0" class="text-center py-12 text-gray-500">
      沒有找到符合條件的小說。
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <NovelCard v-for="novel in novels" :key="novel.id" :novel="novel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../api/axios';
import type { Novel } from '../types';
import NovelCard from '../components/NovelCard.vue';

const novels = ref<Novel[]>([]);
const isLoading = ref(true);
const searchQuery = ref('');
const selectedCategory = ref('ALL');
const selectedStatus = ref('ALL');
let searchTimeout: ReturnType<typeof setTimeout>;

// Removed unused getCategoryLabel and formatDate functions as they are handled by NovelCard or not used.

const fetchNovels = async () => {
  isLoading.value = true;
  try {
    const params: any = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (selectedCategory.value !== 'ALL') params.category = selectedCategory.value;
    if (selectedStatus.value !== 'ALL') params.status = selectedStatus.value;
    
    const response = await apiClient.get<Novel[]>('/novels/', { params });
    // DRF may return paginated data { results: [...], count: ... } or just [...]
    const results = Array.isArray(response.data) ? response.data : (response.data as any).results;
    novels.value = results || [];
  } catch (error) {
    console.error('Failed to fetch novels', error);
  } finally {
    isLoading.value = false;
  }
};

const handleSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchNovels();
  }, 500);
};

onMounted(fetchNovels);
</script>