<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-white">最近更新</h1>

    <div v-if="isLoading" class="text-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
    </div>

    <!-- Grid Layout using NovelCard -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <NovelCard 
            v-for="novel in novels" 
            :key="novel.id" 
            :novel="novel" 
        />
    </div>
    
    <div v-if="!isLoading && novels.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        目前沒有更新紀錄。
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