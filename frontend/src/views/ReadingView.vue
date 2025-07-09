<template>
  <div 
    class="min-h-screen transition-colors duration-300"
    :style="{ backgroundColor: settings.bgColor, color: settings.fontColor }"
  >
    <div class="max-w-3xl mx-auto">
      <div v-if="isLoading" class="text-center py-20">載入中...</div>
      <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>
      
      <div v-else-if="chapter">
        <!-- 頂部導覽 (黏性) -->
        <div class="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md transition-colors duration-300">
          <div class="p-2 sm:p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <router-link :to="`/novel/${novelId}`" class="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </router-link>
            <h1 class="text-lg sm:text-xl font-bold text-center truncate px-2">{{ chapter.title }}</h1>
            <button @click="toggleSettingsPanel" class="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </button>
          </div>
        </div>

        <!-- 小說內容 -->
        <div class="p-6 sm:p-8 lg:p-10">
          <div 
            class="prose max-w-none whitespace-pre-wrap transition-all duration-300"
            :style="{ fontSize: `${settings.fontSize}px` }"
            v-html="displayedContent"
          >
          </div>
        </div>

        <!-- 底部翻頁 -->
        <div class="p-4 flex justify-between items-center">
          <button @click="goToChapter('prev')" :disabled="!chapter.previous_chapter_id" class="btn-icon-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /></svg>
          </button>
          <div class="flex items-center space-x-2 sm:space-x-4">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn-icon-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
            </button>
            <select v-model="currentPage" class="page-select">
              <option v-for="pageNumber in totalPages" :key="pageNumber" :value="pageNumber">
                {{ pageNumber }} / {{ totalPages }}
              </option>
            </select>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-icon-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" /></svg>
            </button>
          </div>
          <button @click="goToChapter('next')" :disabled="!chapter.next_chapter_id" class="btn-icon-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 閱讀設定面板 -->
    <transition name="slide-up">
      <div v-if="showSettingsPanel" class="fixed inset-0 bg-black/40 z-20" @click="showSettingsPanel = false"></div>
    </transition>
    <transition name="slide-up">
      <div v-if="showSettingsPanel" class="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 p-6 shadow-lg border-t dark:border-gray-700 rounded-t-2xl z-30">
        <h3 class="text-lg font-bold mb-4 text-center">閱讀設定</h3>
        
        <!-- 字體大小 -->
        <div class="setting-item">
          <label class="label">字體大小</label>
          <div class="control">
            <button @click="changeFontSize(-1)" class="btn-setting">A-</button>
            <span class="w-12 text-center">{{ settings.fontSize }}px</span>
            <button @click="changeFontSize(1)" class="btn-setting">A+</button>
          </div>
        </div>

        <!-- 背景顏色 -->
        <div class="setting-item">
          <label class="label">閱讀背景</label>
          <div class="control">
            <button v-for="(color, name) in colorThemes" :key="name" 
              @click="changeBgColor(name as string)"
              class="w-8 h-8 rounded-full border-2 transition-transform transform hover:scale-110"
              :class="settings.themeName === name ? 'border-blue-500' : 'border-gray-300 dark:border-gray-600'"
              :style="{ backgroundColor: color.bg }"
            ></button>
          </div>
        </div>

        <div class="mt-6">
            <button @click="showSettingsPanel = false" class="w-full py-2 bg-blue-500 text-white rounded-lg">完成</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, reactive, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/axios';
import { eventBus, EventType } from '../composables/useEventBus';
import { useReadingProgressStore } from '@/store/readingProgress';

const { emit } = eventBus;

interface ChapterContent {
  id: number;
  title: string;
  content: string;
  previous_chapter_id: number | null;
  next_chapter_id: number | null;
}

interface ReadingPosition {
  page: number;
  scroll: number;
}

const props = defineProps({
  novelId: { type: String, required: true },
  chapterId: { type: String, required: true },
});

const router = useRouter();
const chapter = ref<ChapterContent | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const showSettingsPanel = ref(false);

// --- Pagination State ---
const paragraphs = ref<string[]>([]);
const currentPage = ref(1);
const paragraphsPerPage = 30;

const totalPages = computed(() => {
  if (paragraphs.value.length === 0) return 1;
  return Math.ceil(paragraphs.value.length / paragraphsPerPage);
});

const displayedContent = computed(() => {
  const start = (currentPage.value - 1) * paragraphsPerPage;
  const end = start + paragraphsPerPage;
  return paragraphs.value.slice(start, end).join('');
});

// --- Reading Progress (Combined Page and Scroll) ---
const readingProgressStore = useReadingProgressStore();
const progressKey = computed(() => `reading-pos-${props.chapterId}`);

const debounce = (func: Function, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

const saveProgress = () => {
  if (isLoading.value) return;
  const position: ReadingPosition = {
    page: currentPage.value,
    scroll: window.scrollY || document.documentElement.scrollTop,
  };
  try {
    sessionStorage.setItem(progressKey.value, JSON.stringify(position));
    readingProgressStore.saveReadingProgress({
      novelId: props.novelId,
      chapterId: props.chapterId,
      page: currentPage.value,
      timestamp: Date.now(),
    });
  } catch (e) {
    console.error("Failed to save progress to sessionStorage:", e);
  }
};

const handleScroll = debounce(saveProgress, 150);

const restoreProgress = async () => {
  try {
    const savedProgress = sessionStorage.getItem(progressKey.value);
    if (!savedProgress) return;

    const position: ReadingPosition = JSON.parse(savedProgress);

    if (position.page > 0 && position.page <= totalPages.value) {
      currentPage.value = position.page;
    }

    await nextTick(); // Wait for page content to be rendered

    if (position.scroll > 0) {
      const scrollToPosition = () => {
        window.scrollTo({ top: position.scroll, behavior: 'auto' });
      };

      if (document.readyState === 'complete') {
        setTimeout(scrollToPosition, 50);
      } else {
        window.addEventListener('load', scrollToPosition, { once: true });
      }
    }
  } catch (e) {
    console.error("Failed to read progress from sessionStorage:", e);
  }
};

// --- Content Parsing ---
const parseChapterContent = (content: string) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(content, 'text/html');
  const pTags = Array.from(doc.body.querySelectorAll('p'));
  
  if (pTags.length > 0) {
    paragraphs.value = pTags.map(p => p.outerHTML);
  } else {
    paragraphs.value = content.split(/<br\s*\/?>\s*<br\s*\/?>/i).filter(p => p.trim() !== '').map(p => `<p>${p}</p>`);
    if (paragraphs.value.length === 0 && content.trim() !== '') {
        paragraphs.value = [`<p>${content}</p>`];
    }
  }
};

// --- 閱讀設定 --- 
const colorThemes = {
  light: { bg: '#F9FAFB', font: '#111827' }, // 預設白
  sepia: { bg: '#f4e9d8', font: '#5b4636' }, // 泛黃
  gray:  { bg: '#374151', font: '#D1D5DB' }, // 灰色
  dark:  { bg: '#1F2937', font: '#F3F4F6' }, // 深黑
};

const settings = reactive({
  fontSize: 18,
  themeName: 'light',
  bgColor: colorThemes.light.bg,
  fontColor: colorThemes.light.font,
});

const loadSettings = () => {
  const savedSettings = localStorage.getItem('readingSettings');
  if (savedSettings) {
    const parsed = JSON.parse(savedSettings);
    settings.fontSize = parsed.fontSize || 18;
    changeBgColor(parsed.themeName || 'light', false);
  } else {
    const isGlobalDark = document.documentElement.classList.contains('dark');
    changeBgColor(isGlobalDark ? 'dark' : 'light', false);
  }
};

const saveSettings = () => {
  localStorage.setItem('readingSettings', JSON.stringify({ 
    fontSize: settings.fontSize, 
    themeName: settings.themeName 
  }));
};

const changeFontSize = (delta: number) => {
  const newSize = settings.fontSize + delta;
  if (newSize >= 12 && newSize <= 30) {
    settings.fontSize = newSize;
    saveSettings();
  }
};

const changeBgColor = (themeName: string, emitEvent = true) => {
  if (themeName in colorThemes) {
    const theme = colorThemes[themeName as keyof typeof colorThemes];
    settings.themeName = themeName;
    settings.bgColor = theme.bg;
    settings.fontColor = theme.font;
    saveSettings();

    const isDark = themeName === 'dark' || themeName === 'gray';
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    if (emitEvent) {
      emit(EventType.ThemeChanged, isDark ? 'dark' : 'light');
    }
  }
};

// --- API 呼叫與導覽 ---
const fetchChapter = async (nId: string, cId: string) => {
  isLoading.value = true;
  error.value = null;
  currentPage.value = 1;
  try {
    const response = await apiClient.get<ChapterContent>(`/novels/${nId}/chapters/${cId}/`);
    chapter.value = response.data;
    parseChapterContent(chapter.value.content);
    await restoreProgress();
  } catch (err) {
    error.value = '無法載入章節內容。';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

const goToChapter = (direction: 'prev' | 'next') => {
  if (!chapter.value) return;
  const targetChapterId = direction === 'prev' 
    ? chapter.value.previous_chapter_id 
    : chapter.value.next_chapter_id;
  
  if (targetChapterId) {
    router.push({ name: 'Reading', params: { novelId: props.novelId, chapterId: targetChapterId.toString() } });
  }
};

const changePage = () => {
  saveProgress();
  window.scrollTo(0, 0);
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    changePage();
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    changePage();
  }
};

const toggleSettingsPanel = () => {
  showSettingsPanel.value = !showSettingsPanel.value;
};

// --- 生命週期鉤子 ---
onMounted(() => {
  loadSettings();
  fetchChapter(props.novelId, props.chapterId);
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('beforeunload', saveProgress);
});

onUnmounted(() => {
  saveProgress();
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('beforeunload', saveProgress);
});

watch(
  () => props.chapterId,
  (newChapterId, oldChapterId) => {
    if (newChapterId && newChapterId !== oldChapterId) {
      saveProgress();
      fetchChapter(props.novelId, newChapterId);
    }
  }
);

watch(currentPage, () => {
    saveProgress();
    window.scrollTo(0, 0);
});

</script>

<style scoped>
.prose {
  line-height: 1.8;
  color: v-bind('settings.fontColor');
}

.btn-nav {
  @apply flex items-center px-4 py-2 rounded-lg transition-colors duration-200;
  @apply text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-icon-lg {
    @apply p-2 rounded-full transition-colors duration-200;
    @apply text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700;
    @apply disabled:opacity-50 disabled:cursor-not-allowed;
}

.page-select {
    @apply bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm;
    @apply py-2 px-3 text-sm font-medium text-gray-700 dark:text-gray-200;
    @apply focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

/* 動畫效果 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>