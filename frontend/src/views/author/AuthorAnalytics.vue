<!-- src/views/author/AuthorAnalytics.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-6">流量分析</h1>

    <div v-if="isLoading" class="text-center text-gray-500 dark:text-gray-400">載入中...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>

    <div v-else-if="novels.length === 0" class="text-center text-gray-500 dark:text-gray-400">
      <p>您尚未建立任何小說，無法分析流量。</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div 
        v-for="novel in novels" 
        :key="novel.id" 
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-transform duration-300 cursor-pointer"
        @click="selectNovel(novel)"
      >
        <img :src="novel.cover_image || '/placeholder.jpg'" alt="Novel Cover" class="w-full h-48 object-cover">
        <div class="p-4">
          <h2 class="text-xl font-bold truncate text-gray-800 dark:text-white" :title="novel.title">{{ novel.title }}</h2>
        </div>
      </div>
    </div>

    <!-- Analytics Modal -->
    <div v-if="selectedNovel" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="selectedNovel = null">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-11/12 max-w-4xl h-5/6 p-6 flex flex-col">
        <div class="flex justify-between items-center border-b pb-3 mb-4 border-gray-200 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-800 dark:text-white">{{ selectedNovel.title }} - 流量詳情</h2>
          <button @click="selectedNovel = null" class="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-grow overflow-y-auto">
          <!-- Chart will be rendered here -->
          <canvas id="analyticsChart"></canvas>
        </div>
        <!-- Pagination Controls -->
        <div v-if="volumes.length > 1" class="flex justify-center items-center space-x-4 mt-4 py-2 border-t border-gray-200 dark:border-gray-700">
          <button 
            @click="changeVolume(-1)" 
            :disabled="currentVolumeIndex === 0"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg disabled:opacity-50"
          >
            上一卷
          </button>
          <span class="text-gray-600 dark:text-gray-300">
            {{ currentVolumeTitle || 'Loading...' }}
          </span>
          <button 
            @click="changeVolume(1)" 
            :disabled="currentVolumeIndex === volumes.length - 1"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg disabled:opacity-50"
          >
            下一卷
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import apiClient from '../../api/axios';
import type { Novel } from '../../types';
import Chart from 'chart.js/auto';

const novels = ref<Novel[]>([]);
const selectedNovel = ref<Novel | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
let chartInstance: Chart | null = null;

const fetchNovels = async () => {
  isLoading.value = true;
  try {
    // This endpoint should ideally return novels with aggregated view counts
    const response = await apiClient.get('/novels/?my_novels=true&analytics=true'); 
    novels.value = response.data.results;
  } catch (err) {
    console.error(err);
    error.value = '無法載入小說列表。';
  } finally {
    isLoading.value = false;
  }
};

const currentVolumeIndex = ref(0);
const volumes = ref<{ title: string, chapters: { title: string, views: number }[] }[]>([]);
const currentVolumeTitle = ref('');

const selectNovel = async (novel: Novel) => {
  selectedNovel.value = novel;
  await nextTick();
  currentVolumeIndex.value = 0; 
  renderChart(novel);
};

const renderChart = async (novel: Novel) => {
  try {
    const response = await apiClient.get(`/novels/${novel.id}/analytics/`);
    // Assuming backend returns { volumes: [{ title: '...', chapters: [...] }, ...], ... }
    if (response.data.volumes && response.data.volumes.length > 0) {
        volumes.value = response.data.volumes;
    } else {
        // Fallback for flat structure if backend update hasn't propagated or for old novels
        // Construct a pseudo-volume
        volumes.value = [{
            title: '全章節',
            chapters: response.data.labels.map((label: string, i: number) => ({
                title: label,
                views: response.data.data[i]
            }))
        }];
    }
    
    updateChartData();
  } catch (err) {
    console.error('Failed to render chart', err);
  }
};

const updateChartData = () => {
  const ctx = document.getElementById('analyticsChart') as HTMLCanvasElement;
  if (!ctx) return;

  if (chartInstance) {
    chartInstance.destroy();
  }

  const currentVolume = volumes.value[currentVolumeIndex.value];
  currentVolumeTitle.value = currentVolume.title;

  const volumeLabels = currentVolume.chapters.map(c => c.title);
  const volumeData = currentVolume.chapters.map(c => c.views);

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: volumeLabels,
      datasets: [{
        label: '各章節觀看次數',
        data: volumeData,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        title: {
          display: true,
          text: currentVolume.title
        }
      }
    }
  });
};

const changeVolume = (delta: number) => {
  const newIndex = currentVolumeIndex.value + delta;
  if (newIndex >= 0 && newIndex < volumes.value.length) {
    currentVolumeIndex.value = newIndex;
    updateChartData();
  }
};

onMounted(fetchNovels);
</script>
