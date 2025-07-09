<!-- src/views/NovelDetailView.vue -->
<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 pt-8">
    <!-- 載入中骨架屏 (也按照新佈局設計) -->
    <div v-if="isLoading" class="animate-pulse">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
        <!-- 左欄 & 中欄 -->
        <div class="md:col-span-6 lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div class="h-80 bg-gray-300 dark:bg-gray-700 rounded-lg"></div>
          <div class="flex flex-col justify-between">
            <div>
              <div class="h-6 bg-gray-300 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
              <div class="h-10 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
              <div class="h-6 bg-gray-300 dark:bg-gray-700 rounded w-1/2 mt-4"></div>
            </div>
            <div class="h-12 bg-gray-300 dark:bg-gray-700 rounded w-full"></div>
          </div>
        </div>
        <!-- 右欄 -->
        <div class="md:col-span-6 lg:col-span-7 h-80 bg-gray-300 dark:bg-gray-700 rounded-lg p-6"></div>
      </div>
    </div>

    <!-- 錯誤狀態 (保持不變) -->
    <div v-else-if="error" class="text-center py-10 bg-red-100 dark:bg-red-900/20 p-4 rounded-lg">
      <p class="text-red-600 dark:text-red-400 font-semibold text-xl">哦不，出錯了</p>
      <p class="text-red-500 dark:text-red-500 mt-2">{{ error }}</p>
      <router-link to="/" class="mt-6 inline-block px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">返回首頁</router-link>
    </div>

    <!-- 成功載入 - 全新三欄式佈局 -->
    <div v-else-if="novel" class="text-gray-800 dark:text-gray-200">
      <!-- 上方核心資訊區 -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12">
  
        <!-- === 中間欄：封面 (結構簡化) === -->
        <div class="md:col-span-4 lg:col-span-3 flex items-center justify-center md:order-2">
            <img 
              v-if="novel.cover_image"
              :src="novel.cover_image" 
              :alt="novel.title" 
              class="w-full max-w-xs md:max-w-full mx-auto h-auto object-cover rounded-lg shadow-2xl"
            >
            <div v-else class="w-full max-w-xs h-96 flex items-center justify-center bg-gray-200 dark:bg-gray-700 rounded-lg shadow-2xl">
              <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            </div>
        </div>
        
        <!-- === 左側欄：標題 + 作者 + 操作按鈕 (新結構) === -->
        <div class="md:col-span-4 lg:col-span-4 flex flex-col justify-between text-center md:text-left md:order-1">
            <!-- 上半部：文字資訊 -->
            <div>
            <span class="text-base font-semibold px-4 py-1.5 rounded-full inline-block" :class="statusInfo.class">
                {{ statusInfo.text }}
            </span>
            <h1 class="text-5xl lg:text-5xl font-bold mt-4 tracking-tight">{{ novel.title }}</h1>
            <p class="text-xl text-gray-600 dark:text-gray-400 mt-4">
            作者：
            <router-link 
                :to="{ name: 'Author', params: { id: novel.author.user_id } }" 
                class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            >
                {{ novel.author.pen_name || novel.author.username }}
            </router-link>
            </p>
            <p class="text-base text-gray-500 mt-3">
                發布於 {{ new Date(novel.created_at).toLocaleDateString() }}
            </p>
            </div>
            
            <!-- 下半部：操作按鈕 -->
            <div class="mt-8 flex space-x-4 w-full">
                        <button @click="startReading" class="btn-primary flex-1">{{ readingButtonText }}</button>
            <button 
                @click="toggleBookshelf"
                class="btn-secondary flex-1"
            >
                {{ isInBookshelf ? '從書架移除' : '加入書架' }}
            </button>
            </div>
        </div>
        
        <!-- === 右側欄：故事簡介 (保持不變) === -->
        <div class="md:col-span-4 lg:col-span-5 bg-white dark:bg-gray-800/50 p-6 rounded-lg shadow-sm flex flex-col md:order-3 h-full">
            <h2 class="text-xl font-bold border-b border-gray-200 dark:border-gray-700 pb-2 mb-4 flex-shrink-0">故事簡介</h2>
            <div class="overflow-y-auto flex-grow">
            <p class="whitespace-pre-wrap leading-relaxed">
                {{ novel.description }}
            </p>
            </div>
        </div>

        </div>

      <!-- 下方章節目錄區 -->
      <div class="mt-12">
        <h2 class="text-xl font-bold mb-4">章節目錄</h2>
        <div v-if="novel.volumes.length > 0 || (novel.chapters_without_volume && novel.chapters_without_volume.length > 0)" class="bg-white dark:bg-gray-800/50 rounded-lg shadow-sm overflow-hidden">
          <!-- 分卷列表 -->
          <div v-for="volume in novel.volumes" :key="volume.id" class="mb-4 last:mb-0">
            <h3 class="text-lg font-semibold bg-gray-100 dark:bg-gray-700 px-6 py-3 border-b border-gray-200 dark:border-gray-700">
              {{ volume.title }}
            </h3>
            <ul>
              <li v-for="chapter in volume.chapters" :key="chapter.id" class="border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                <router-link 
                  :to="`/read/${novel.id}/${chapter.id}`"
                  class="block px-6 py-4 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors duration-200"
                >
                  <div class="flex justify-between items-center">
                    <span class="text-gray-800 dark:text-gray-200">{{ chapter.title }}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ new Date(chapter.published_at).toLocaleDateString() }}</span>
                  </div>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- 未分卷章節列表 -->
          <div v-if="novel.chapters_without_volume && novel.chapters_without_volume.length > 0">
            <h3 v-if="novel.volumes.length > 0" class="text-lg font-semibold bg-gray-100 dark:bg-gray-700 px-6 py-3 border-t border-gray-200 dark:border-gray-700">
              未分卷章節
            </h3>
            <ul>
              <li v-for="chapter in novel.chapters_without_volume" :key="chapter.id" class="border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                <router-link 
                  :to="`/read/${novel.id}/${chapter.id}`"
                  class="block px-6 py-4 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors duration-200"
                >
                  <div class="flex justify-between items-center">
                    <span class="text-gray-800 dark:text-gray-200">{{ chapter.title }}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ new Date(chapter.published_at).toLocaleDateString() }}</span>
                  </div>
                </router-link>
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="text-center py-10 text-gray-500">
          作者還沒有發布任何章節或分卷。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// --- SCRIPT 區塊完全不需要修改，保持原樣 ---
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios';
import type { Novel, Chapter } from '../types';
import { useAuthStore } from '@/store/auth';
import { eventBus, EventType } from '@/composables/useEventBus';

interface ReadingProgress {
  novelId: string;
  chapterId: string;
  page: number;
  timestamp: number;
}

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
});

const novel = ref<Novel | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const authStore = useAuthStore();
const isInBookshelf = ref(false);
const router = useRouter();
const readingProgress = ref<ReadingProgress | null>(null);

const loadReadingProgress = () => {
  const savedProgress = localStorage.getItem(`readingProgress_${props.id}`);
  if (savedProgress) {
    readingProgress.value = JSON.parse(savedProgress);
  } else {
    readingProgress.value = null;
  }
};

const fetchNovelDetail = async (novelId: string) => {
  console.log(`[NovelDetailView] Fetching novel with ID: ${novelId}`);
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Novel>(`/novels/${novelId}/`);
    novel.value = response.data;
    console.log("[NovelDetailView] Received novel data:", novel.value);
    loadReadingProgress(); // Load reading progress after novel details are fetched
    // 檢查是否在書架中
    if (authStore.isAuthenticated) {
      const bookshelfResponse = await apiClient.get(`/reading-progress/?novel=${novelId}`);
      isInBookshelf.value = bookshelfResponse.data.count > 0;
    }
  } catch (err: any) {
    console.error("[NovelDetailView] Error fetching novel:", err);
    if (err.response?.status === 404) {
      error.value = "找不到這本小說。";
    } else {
      error.value = "無法載入小說資料，請稍後再試。";
    }
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.id, (newId) => {
  if (newId) {
    fetchNovelDetail(newId);
  }
});


const readingButtonText = computed(() => {
  if (!novel.value || !readingProgress.value) return '開始閱讀';

  const chapterIdToFind = readingProgress.value.chapterId;
  let foundChapter: Chapter | undefined;

  // Search in volumes
  for (const volume of novel.value.volumes) {
    foundChapter = volume.chapters.find(c => c.id.toString() === chapterIdToFind);
    if (foundChapter) break;
  }

  // If not found, search in chapters_without_volume
  if (!foundChapter && novel.value.chapters_without_volume) {
    foundChapter = novel.value.chapters_without_volume.find(c => c.id.toString() === chapterIdToFind);
  }

  if (foundChapter) {
    return `續看 ${foundChapter.title}`;
  }
  
  return '開始閱讀';
});

const toggleBookshelf = async () => {
  if (!authStore.isAuthenticated) {
    eventBus.emit(EventType.ShowAlert, {
      type: 'warning',
      title: '提示',
      message: '請先登入才能加入書架。',
    });
    return;
  }
  if (!novel.value) return;

  try {
    if (isInBookshelf.value) {
      // 從書架移除
      const response = await apiClient.get(`/reading-progress/?novel=${novel.value.id}`);
      if (response.data.results.length > 0) {
        const progressId = response.data.results[0].id;
        await apiClient.delete(`/reading-progress/${progressId}/`);
        isInBookshelf.value = false;
        eventBus.emit(EventType.ShowAlert, {
          type: 'success',
          title: '成功',
          message: '已從書架移除。',
        });
      }
    } else {
      // 加入書架
      await apiClient.post('/reading-progress/', { novel: novel.value.id });
      isInBookshelf.value = true;
      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '已加入書架。',
      });
    }
  } catch (err) {
    console.error('書架操作失敗', err);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '書架操作失敗，請稍後再試。',
    });
  }
};



const statusInfo = computed(() => {
  if (!novel.value) return { text: '', class: '' };
  switch (novel.value.status) {
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

onMounted(() => {
  fetchNovelDetail(props.id);
});

const startReading = async () => {
  if (!novel.value) return;

  let targetChapterId: number | string | undefined;

  // 1. Check for saved progress
  if (readingProgress.value && readingProgress.value.novelId === props.id) {
    targetChapterId = readingProgress.value.chapterId;
  } else {
    // 2. Find the first chapter of the first volume
    if (novel.value.volumes && novel.value.volumes.length > 0 && novel.value.volumes[0].chapters.length > 0) {
      targetChapterId = novel.value.volumes[0].chapters[0].id;
    } 
    // 3. If no volumes, find the first chapter without a volume
    else if (novel.value.chapters_without_volume && novel.value.chapters_without_volume.length > 0) {
      targetChapterId = novel.value.chapters_without_volume[0].id;
    }
  }

  if (targetChapterId) {
    router.push({ 
      name: 'Reading', 
      params: { novelId: novel.value.id, chapterId: targetChapterId },
    });
  } else {
    eventBus.emit(EventType.ShowAlert, {
      type: 'info',
      title: '提示',
      message: '這本小說還沒有任何章節。',
    });
  }
};
</script>

<style scoped>
/* 我們可以讓按鈕樣式更統一 */
.btn-primary, .btn-secondary {
  @apply font-semibold py-3 px-6 rounded-lg shadow-md transition-transform transform hover:scale-105 disabled:opacity-50 text-center;
}
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white;
}
.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
</style>
