<template>
  <div 
    class="min-h-screen"
    :style="{ backgroundColor: settings.bgColor, color: settings.fontColor }"
  >
      <div :class="[containerWidthClass, 'mx-auto']">
      <div v-if="isLoading" class="text-center py-20">載入中...</div>
      <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>
      
      <div v-else-if="chapter">
        <!-- 頂部導覽 (黏性) -->
        <div 
          class="sticky top-0 z-10 shadow-sm transition-transform duration-300"
          :style="{ backgroundColor: settings.themeName === 'dark' ? 'rgba(31, 41, 55, 0.95)' : settings.bgColor }"
        >
          <div class="p-2 sm:p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <router-link :to="`/novel/${novelId}`" class="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </router-link>
            <h1 class="text-lg sm:text-xl font-bold text-center truncate px-2">{{ chapter.title }}</h1>
            <div class="relative">
              <button @click="toggleSettingsPanel" class="btn-icon relative z-50">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </button>
              
              <!-- Settings Panel (Desktop Dropdown Style) -->
              <transition
                enter-active-class="transition ease-out duration-200 transform origin-top-right"
                enter-from-class="opacity-0 scale-95"
                enter-to-class="opacity-100 scale-100"
                leave-active-class="transition ease-in duration-150 transform origin-top-right"
                leave-from-class="opacity-100 scale-100"
                leave-to-class="opacity-0 scale-95"
              >
                <div v-if="showSettingsPanel" class="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 p-6 shadow-xl border border-gray-100 dark:border-gray-700 rounded-xl z-40">
                  <h3 class="text-lg font-bold mb-4 text-left text-gray-800 dark:text-white">閱讀設定</h3>
                  
                  <!-- 字體大小 -->
                  <div class="setting-item">
                    <label class="label">字體大小</label>
                    <div class="control">
                      <button @click="changeFontSize(-1)" class="btn-setting">A-</button>
                      <span class="w-12 text-center text-gray-800 dark:text-gray-200">{{ settings.fontSize }}px</span>
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

                  <!-- 版面寬度 (電腦版) -->
                  <div class="setting-item hidden sm:flex">
                     <label class="label">版面寬度</label>
                     <div class="control text-sm">
                        <button @click="settings.widthMode = 'small'; saveSettings()" :class="{'bg-blue-500 text-white': settings.widthMode === 'small'}" class="px-2 py-1 rounded border border-gray-300 dark:border-gray-600 transition-colors">標準</button>
                        <button @click="settings.widthMode = 'large'; saveSettings()" :class="{'bg-blue-500 text-white': settings.widthMode === 'large'}" class="px-2 py-1 rounded border border-gray-300 dark:border-gray-600 transition-colors">寬版</button>
                        <button @click="settings.widthMode = 'full'; saveSettings()" :class="{'bg-blue-500 text-white': settings.widthMode === 'full'}" class="px-2 py-1 rounded border border-gray-300 dark:border-gray-600 transition-colors">滿版</button>
                     </div>
                  </div>

                  <div class="mt-6 flex justify-end">
                      <button @click="showSettingsPanel = false" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">關閉</button>
                  </div>
                </div>
              </transition>
            </div>
            
            <!-- Mobile Backdrop for settings -->
             <div v-if="showSettingsPanel" class="fixed inset-0 z-30" @click="showSettingsPanel = false"></div>
          </div>
        </div>

        <!-- 小說內容 -->
        <div class="p-6 sm:p-8 lg:p-10">
          <div 
            class="prose max-w-none whitespace-pre-wrap"
            :style="{ fontSize: `${settings.fontSize}px` }"
            v-html="displayedContent"
          >
          </div>
        </div>

        <!-- 底部翻頁 -->
        <div class="p-4 flex justify-between items-center gap-2">
          <button @click="goBackward" :disabled="isFirstPage && !chapter.previous_chapter_id" class="btn-nav-lg flex-1">
            {{ isFirstPage ? '上一章' : '上一頁' }}
          </button>
          
          <button @click="openPageSelector" class="btn-nav-lg flex-[2] font-medium border-l border-r border-gray-300 dark:border-gray-600">
             第 {{ currentPage }} / {{ totalPages }} 頁
          </button>

          <button @click="goForward" :disabled="isLastPage && !chapter.next_chapter_id" class="btn-nav-lg flex-1">
            {{ isLastPage ? '下一章' : '下一頁' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Page Selection Modal -->
    <Modal :show="showPageSelector" @close="showPageSelector = false">
      <template #header>跳轉頁面</template>
      <template #body>
        <div class="grid grid-cols-4 sm:grid-cols-5 gap-3 max-h-[60vh] overflow-y-auto p-1">
          <button 
            v-for="pageNumber in totalPages" 
            :key="pageNumber" 
            @click="selectPage(pageNumber)"
            class="p-2 rounded-lg text-sm font-medium transition-colors"
            :class="pageNumber === currentPage 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'"
          >
            {{ pageNumber }}
          </button>
        </div>
      </template>
    </Modal>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, reactive, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/axios';
import { eventBus, EventType } from '../composables/useEventBus';
import { useReadingProgressStore } from '@/store/readingProgress';
import Modal from '../components/Modal.vue';
import { useAutoHideNavbar } from '../composables/useAutoHideNavbar';

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
const showPageSelector = ref(false); // New state for modal

// Scroll restoration state
const shouldRestoreScroll = ref(true); // Default to true (for refresh/initial load)
const restoreToBottom = ref(false); // Flag for previous chapter navigation

// --- Pagination State ---
const paragraphs = ref<string[]>([]);
const currentPage = ref(1);
const paragraphsPerPage = 30;
const isManualPagination = ref(false); // Flag for manual page breaks

const totalPages = computed(() => {
  if (paragraphs.value.length === 0) return 1;
  if (isManualPagination.value) return paragraphs.value.length;
  return Math.ceil(paragraphs.value.length / paragraphsPerPage);
});

const displayedContent = computed(() => {
  if (isManualPagination.value) {
      // In manual mode, paragraphs array ARE the pages
      return paragraphs.value[currentPage.value - 1] || '';
  }
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
    // Logic to handle restoreToBottom (Previous Chapter)
    if (restoreToBottom.value) {
        currentPage.value = totalPages.value; // Jump to last page
        await nextTick();
        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'auto' });
            shouldRestoreScroll.value = true;
            restoreToBottom.value = false;
        }, 100);
        return; // Skip standard restore logic
    }

    if (!shouldRestoreScroll.value) return; // Skip if manually navigating

    try {
    const savedProgress = sessionStorage.getItem(progressKey.value);
    
    // Default scroll to top if not restoring
    let targetScroll = 0;
    
    if (savedProgress) {
      const position: ReadingPosition = JSON.parse(savedProgress);
      if (position.page > 0 && position.page <= totalPages.value) {
        currentPage.value = position.page;
      }
      targetScroll = position.scroll;
    }

    await nextTick();

    const scrollToPosition = () => {
        window.scrollTo({ top: targetScroll, behavior: 'auto' });
    };

    if (document.readyState === 'complete') {
        setTimeout(scrollToPosition, 50);
    } else {
        window.addEventListener('load', scrollToPosition, { once: true });
    }

  } catch (e) {
    console.error("Failed to read progress to sessionStorage:", e);
  }
};

// --- Content Parsing ---
const parseChapterContent = (content: string) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(content, 'text/html');
  
  // Custom Page Breaks Priority
  const breaks = doc.querySelectorAll('hr[data-type="page-break"]');
  
  if (breaks.length > 0) {
      isManualPagination.value = true;
      // Remove unused rawHtml if not used
      // const rawHtml = content; 
 
      // doc.body.innerHTML might have changed format slightly by parser, but usually safer for consistency
      // However, spliting by the tag needs to match.
      // Let's use doc.body.innerHTML and a regex that matches valid HR
      
      const segments = doc.body.innerHTML.split(/<hr[^>]*data-type="page-break"[^>]*>/i);
      paragraphs.value = segments.map(seg => seg.trim()).filter(seg => seg.length > 0);
      
      if (paragraphs.value.length === 0) {
           paragraphs.value = [doc.body.innerHTML]; // Fallback if split failed weirdly
      }
  } else {
      isManualPagination.value = false;
      const pTags = Array.from(doc.body.querySelectorAll('p'));
      
      if (pTags.length > 0) {
        paragraphs.value = pTags.map(p => p.outerHTML);
      } else {
        paragraphs.value = content.split(/<br\s*\/?>\s*<br\s*\/?>/i).filter(p => p.trim() !== '').map(p => `<p>${p}</p>`);
        if (paragraphs.value.length === 0 && content.trim() !== '') {
            paragraphs.value = [`<p>${content}</p>`];
        }
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
  widthMode: 'small' as 'small' | 'large' | 'full',
});

const containerWidthClass = computed(() => {
    switch (settings.widthMode) {
        case 'large': return 'max-w-[90%] sm:max-w-6xl md:max-w-7xl';
        case 'full': return 'max-w-full px-4';
        default: return 'max-w-3xl'; // small
    }
});

const loadSettings = () => {
  const savedSettings = localStorage.getItem('readingSettings');
  if (savedSettings) {
    const parsed = JSON.parse(savedSettings);
    settings.fontSize = parsed.fontSize || 18;
    settings.widthMode = parsed.widthMode || 'small';
    changeBgColor(parsed.themeName || 'light', false);
  } else {
    const isGlobalDark = document.documentElement.classList.contains('dark');
    changeBgColor(isGlobalDark ? 'dark' : 'light', false);
  }
};

const saveSettings = () => {
  localStorage.setItem('readingSettings', JSON.stringify({ 
    fontSize: settings.fontSize, 
    themeName: settings.themeName,
    widthMode: settings.widthMode
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
    
    const applyTheme = () => {
        const theme = colorThemes[themeName as keyof typeof colorThemes];
        settings.themeName = themeName;
        settings.bgColor = theme.bg;
        settings.fontColor = theme.font;
        saveSettings();

        const isDark = themeName === 'dark' || themeName === 'gray';
        
        document.documentElement.classList.add('no-transition');

        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }

        void document.documentElement.offsetHeight; 
        
        setTimeout(() => {
            document.documentElement.classList.remove('no-transition');
        }, 0);

        if (emitEvent) {
          emit(EventType.ThemeChanged, isDark ? 'dark' : 'light');
        }
    };

    if (document.startViewTransition && emitEvent) {
         document.startViewTransition(() => {
             applyTheme();
         });
    } else {
        applyTheme();
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
    if (direction === 'prev') {
        restoreToBottom.value = true;
    } else {
        shouldRestoreScroll.value = false; // Next chapter should start at top, disable restore
        // Force reset
        window.scrollTo({ top: 0, behavior: 'instant' });
    }
    router.push({ name: 'Reading', params: { novelId: props.novelId, chapterId: targetChapterId.toString() } });
  }
};

const isFirstPage = computed(() => currentPage.value === 1);
const isLastPage = computed(() => currentPage.value === totalPages.value);

const goForward = () => {
  if (!isLastPage.value) {
    currentPage.value++;
    window.scrollTo({ top: 0, behavior: 'instant' });
  } else if (chapter.value && chapter.value.next_chapter_id) {
    goToChapter('next');
  }
};

const goBackward = () => {
  if (!isFirstPage.value) {
      currentPage.value--;
      // User requested scroll to bottom on prev page
      nextTick(() => {
         window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }); 
      });
  } else if (chapter.value && chapter.value.previous_chapter_id) {
    goToChapter('prev');
  }
};

const toggleSettingsPanel = () => {
  showSettingsPanel.value = !showSettingsPanel.value;
};

// --- New Modal Logic ---
const openPageSelector = () => {
  showPageSelector.value = true;
};

const selectPage = (page: number) => {
  currentPage.value = page;
  showPageSelector.value = false;
  window.scrollTo({ top: 0, behavior: 'instant' }); // Scroll to top when page changes via modal
};


// --- Auto-Hide Navbar Logic ---
useAutoHideNavbar();

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

watch(currentPage, (newPage, oldPage) => {
    if (newPage !== oldPage) {
        saveProgress();
        // Scroll logic is now handled in actions (goForward/goBackward/selectPage)
        // to support different behaviors (top vs bottom)
    }
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

.btn-setting {
    @apply w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg;
    @apply bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600;
    @apply border border-gray-300 dark:border-gray-600; /* Add border for contrast */
}

.btn-icon-lg {
    @apply p-2 rounded-full transition-colors duration-200;
    @apply text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700;
    @apply disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-nav-lg {
  @apply h-12 flex items-center justify-center rounded-lg transition-colors duration-200 text-sm sm:text-base;
  @apply bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600;
  @apply text-gray-700 dark:text-gray-200;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
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