<template>
  <div 
    ref="pageContainer"
    class="flip-reading-view"
    :style="pageContainerStyle"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center h-screen">
      <div class="text-lg" :style="{ color: effectiveTextColor }">載入中...</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center h-screen">
      <div class="text-red-500 text-lg">{{ error }}</div>
    </div>

    <!-- Content -->
    <div v-else-if="chapter" class="h-screen flex flex-col overflow-hidden">
      <!-- Header Bar with Progress Indicator -->
      <div 
        class="flex-shrink-0 relative"
        :style="{ backgroundColor: effectiveContentBg }"
      >
        <!-- Progress Bar (bottom of header) -->
        <div 
          class="absolute bottom-0 left-0 h-0.5 bg-blue-500/70 transition-all duration-300 ease-out"
          :style="{ width: progressPercentage + '%' }"
        ></div>
        <!-- Header Content -->
        <div class="flex items-center justify-between px-4 py-1">
          <router-link :to="`/novel/${novelId}`" class="p-2 rounded-full hover:bg-black/10 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" :stroke="effectiveTextColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </router-link>
          
          <!-- Title and Page Count -->
          <button 
            @click="showPageSelector = true"
            class="flex-1 px-2 text-center hover:bg-black/5 rounded-lg py-1 transition-colors"
          >
            <h1 
              class="text-sm font-medium truncate"
              :style="{ color: effectiveTextColor }"
            >
              {{ chapter.title }}
            </h1>
            <span 
              class="text-xs opacity-60"
              :style="{ color: effectiveTextColor }"
            >
              {{ currentPage }} / {{ totalPages }}
            </span>
          </button>
          
          <button @click="showSettings = true" class="p-2 rounded-full hover:bg-black/10 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" :stroke="effectiveTextColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Main Content Area with CSS Columns -->
      <div class="flex-1 relative overflow-hidden" ref="contentArea">
        <!-- Left Tap Zone -->
        <div 
          class="absolute left-0 top-0 w-[30%] h-full z-20 cursor-pointer"
          @click="goPrevPage"
        ></div>
        
        <!-- Right Tap Zone -->
        <div 
          class="absolute right-0 top-0 w-[30%] h-full z-20 cursor-pointer"
          @click="goNextPage"
        ></div>

        <!-- Content Viewport -->
        <div class="w-full h-full overflow-hidden relative px-4 py-2">
          <!-- Content Slider (transforms to show different pages) -->
          <div 
            class="h-full transition-transform duration-300 ease-out will-change-transform"
            :class="{ 'opacity-0': !layoutReady, 'opacity-100': layoutReady }"
            :style="sliderStyle"
          >
            <!-- Column Container (CSS Columns magic happens here) -->
            <div 
              ref="columnContainer"
              class="prose max-w-none h-full column-container transition-opacity duration-200"
              :style="columnStyle"
            >
              <div v-html="fullChapterContent"></div>
            </div>
          </div>
          <!-- Loading indicator while layout is calculating -->
          <div 
            v-if="!layoutReady" 
            class="absolute inset-0 flex items-center justify-center"
            :style="{ backgroundColor: effectiveContentBg }"
          >
            <div class="text-sm opacity-60" :style="{ color: effectiveTextColor }">排版中...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Panel Overlay - Dropdown Style -->
    <transition
      enter-active-class="transition ease-out duration-200 transform origin-top-right"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150 transform origin-top-right"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showSettings" class="fixed inset-0 z-50">
        <!-- Backdrop -->
        <div class="absolute inset-0" @click="showSettings = false"></div>
        <!-- Panel -->
        <div class="absolute right-4 top-12 w-80 max-w-[calc(100vw-2rem)] bg-white dark:bg-gray-800 shadow-xl border border-gray-100 dark:border-gray-700 rounded-xl max-h-[80vh] overflow-y-auto">
          <div class="p-6">
            <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">閱讀設定</h3>

            <!-- Font Size -->
            <div class="setting-item">
              <label class="label">字體大小</label>
              <div class="control">
                <button @click="changeFontSize(-1)" class="btn-setting">A-</button>
                <span class="w-12 text-center text-gray-800 dark:text-gray-200">{{ settings.fontSize }}px</span>
                <button @click="changeFontSize(1)" class="btn-setting">A+</button>
              </div>
            </div>

            <!-- Custom Color Toggle -->
            <div class="setting-item">
              <label class="label">自定義配色</label>
              <button 
                @click="settings.customColorEnabled = !settings.customColorEnabled; saveSettings()"
                class="toggle-switch"
                :class="settings.customColorEnabled ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'"
              >
                <span class="toggle-knob" :class="settings.customColorEnabled ? 'translate-x-[18px]' : 'translate-x-[2px]'"></span>
              </button>
            </div>

            <!-- Preset Themes (when custom disabled) -->
            <div v-if="!settings.customColorEnabled" class="setting-item">
              <label class="label">顏色</label>
              <div class="control gap-1">
                <button v-for="(color, name) in colorThemes" :key="name" 
                  @click="changeBgColor(name as string)"
                  class="w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 flex-shrink-0"
                  :class="settings.themeName === name ? 'border-blue-500' : 'border-gray-300 dark:border-gray-600'"
                  :style="{ backgroundColor: color.bg }"
                  :title="getThemeName(name as string)"
                ></button>
              </div>
            </div>

            <!-- Custom Color Pickers -->
            <div v-if="settings.customColorEnabled" class="mt-4 space-y-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-300">閱讀底色</span>
                <div class="flex items-center gap-2">
                  <input type="color" v-model="settings.customContentBg" @change="saveSettings" class="w-8 h-8 rounded cursor-pointer border-0">
                  <span class="text-xs text-gray-500 font-mono">{{ settings.customContentBg }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-300">文字顏色</span>
                <div class="flex items-center gap-2">
                  <input type="color" v-model="settings.customTextColor" @change="saveSettings" class="w-8 h-8 rounded cursor-pointer border-0">
                  <span class="text-xs text-gray-500 font-mono">{{ settings.customTextColor }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-600">
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-600 dark:text-gray-300">文字外框</span>
                  <button 
                    @click="settings.textOutlineEnabled = !settings.textOutlineEnabled; saveSettings()"
                    class="toggle-switch-sm"
                    :class="settings.textOutlineEnabled ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-500'"
                  >
                    <span class="toggle-knob-sm" :class="settings.textOutlineEnabled ? 'translate-x-[14px]' : 'translate-x-[2px]'"></span>
                  </button>
                </div>
                <input v-if="settings.textOutlineEnabled" type="color" v-model="settings.textOutlineColor" @change="saveSettings" class="w-6 h-6 rounded cursor-pointer border-0">
              </div>
              <button @click="resetCustomColors" class="w-full py-1.5 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                重置為預設
              </button>
            </div>

            <div class="border-t border-gray-200 dark:border-gray-700 my-4"></div>

            <!-- Switch to Standard Reading -->
            <button 
              @click="router.push(`/read/${novelId}/${chapterId}`)"
              class="w-full py-2.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
            >
              切換到標準閱讀模式
            </button>

            <!-- Close Button -->
            <button 
              @click="showSettings = false"
              class="mt-4 w-full py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              關閉
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Page Selector Modal -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showPageSelector" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showPageSelector = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-xl p-6 max-w-sm w-full mx-4 max-h-[70vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">選擇頁面</h3>
          <div class="grid grid-cols-5 gap-2">
            <button 
              v-for="page in totalPages" 
              :key="page"
              @click="goToPage(page)"
              class="py-2 text-center rounded-lg transition-colors text-sm"
              :class="page === currentPage ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'"
            >
              {{ page }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios';

interface ChapterContent {
  id: number;
  title: string;
  content: string;
  novel_id: number;
  next_chapter_id: number | null;
  previous_chapter_id: number | null;
}

const props = defineProps<{
  novelId: string;
  chapterId: string;
}>();

const router = useRouter();

// State
const chapter = ref<ChapterContent | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const showSettings = ref(false);
const showPageSelector = ref(false);
const layoutReady = ref(false); // Hide content until CSS columns are ready

// Content and pagination (CSS Columns based)
const currentPage = ref(1);
const totalPages = ref(1);
const containerWidth = ref(0);
const columnGap = 32; // Gap between columns in px
const contentArea = ref<HTMLElement | null>(null);
const columnContainer = ref<HTMLElement | null>(null);

// Touch handling
const touchStartX = ref(0);

// Color themes
const colorThemes = {
  light: { bg: '#F9FAFB', font: '#111827' },
  sepia: { bg: '#f4e9d8', font: '#5b4636' },
  gray:  { bg: '#374151', font: '#D1D5DB' },
  dark:  { bg: '#1F2937', font: '#F3F4F6' },
  amoled: { bg: '#000000', font: '#E5E5E5' },
};

// Settings
const settings = reactive({
  fontSize: 18,
  themeName: 'light',
  bgColor: colorThemes.light.bg,
  fontColor: colorThemes.light.font,
  customColorEnabled: false,
  customContentBg: '#FFFFFF',
  customTextColor: '#111827',
  textOutlineEnabled: false,
  textOutlineColor: '#000000',
});

// Computed colors
const effectivePageBg = computed(() => 
  settings.customColorEnabled ? settings.customContentBg : settings.bgColor
);

const effectiveContentBg = computed(() => 
  settings.customColorEnabled ? settings.customContentBg : settings.bgColor
);

const effectiveTextColor = computed(() => 
  settings.customColorEnabled ? settings.customTextColor : settings.fontColor
);

// Full chapter content (render entire chapter, not just current page)
const fullChapterContent = computed(() => {
  if (!chapter.value) return '';
  return chapter.value.content;
});

// Progress percentage
const progressPercentage = computed(() => 
  totalPages.value > 0 ? (currentPage.value / totalPages.value) * 100 : 0
);

// Styles
const pageContainerStyle = computed(() => ({
  backgroundColor: effectivePageBg.value,
}));

// Slider style - controls transform to show different pages
const sliderStyle = computed(() => {
  const pageIndex = currentPage.value - 1;
  const translateX = (containerWidth.value + columnGap) * pageIndex;
  return {
    transform: `translateX(-${translateX}px)`,
    width: '100%',
  };
});

// Column style - CSS Columns magic
const columnStyle = computed(() => {
  const style: Record<string, string> = {
    height: '100%',
    width: '100%',
    columnWidth: `${containerWidth.value}px`,
    columnGap: `${columnGap}px`,
    columnFill: 'auto', // Critical: fill column before moving to next
    fontSize: `${settings.fontSize}px`,
    color: effectiveTextColor.value,
    lineHeight: '1.8',
  };
  
  if (settings.textOutlineEnabled && settings.customColorEnabled) {
    const c = settings.textOutlineColor;
    style.textShadow = `-0.5px -0.5px 0 ${c}, 0.5px -0.5px 0 ${c}, -0.5px 0.5px 0 ${c}, 0.5px 0.5px 0 ${c}`;
  }
  
  return style;
});

// Calculate layout and total pages
const updateLayout = () => {
  if (!contentArea.value || !columnContainer.value) return;
  
  // Get container width (subtract padding: px-4 = 16px * 2)
  const fullWidth = contentArea.value.clientWidth;
  containerWidth.value = fullWidth - 32; // 16px padding on each side
  
  // Wait for DOM to update with new column width
  nextTick(() => {
    if (!columnContainer.value) return;
    
    // Get total scroll width (includes all columns)
    const scrollW = columnContainer.value.scrollWidth;
    const singlePageW = containerWidth.value + columnGap;
    
    // Calculate total pages
    const pages = Math.ceil((scrollW + columnGap) / singlePageW);
    totalPages.value = Math.max(1, pages);
    
    // Ensure current page is valid
    if (currentPage.value > totalPages.value) {
      currentPage.value = totalPages.value;
    }
    
    // Mark layout as ready to show content
    layoutReady.value = true;
  });
};

// Navigation
const goPrevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    savePageProgress();
  } else if (chapter.value?.previous_chapter_id) {
    router.push(`/read/${props.novelId}/${chapter.value.previous_chapter_id}/flip`);
  }
};

const goNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    savePageProgress();
  } else if (chapter.value?.next_chapter_id) {
    router.push(`/read/${props.novelId}/${chapter.value.next_chapter_id}/flip`);
  }
};

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    showPageSelector.value = false;
    savePageProgress();
  }
};

// Page progress persistence
const getPageProgressKey = () => `flip-page-${props.novelId}-${props.chapterId}`;

const savePageProgress = () => {
  const key = getPageProgressKey();
  localStorage.setItem(key, currentPage.value.toString());
};

const restorePageProgress = () => {
  const key = getPageProgressKey();
  const savedPage = localStorage.getItem(key);
  if (savedPage) {
    const page = parseInt(savedPage, 10);
    if (page > 0 && page <= totalPages.value) {
      currentPage.value = page;
    }
  }
};

// Touch handling for swipe
const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0].clientX;
};

const handleTouchEnd = (e: TouchEvent) => {
  const touchEndX = e.changedTouches[0].clientX;
  const diff = touchStartX.value - touchEndX;
  
  if (Math.abs(diff) > 50) {
    if (diff > 0) {
      goNextPage();
    } else {
      goPrevPage();
    }
  }
};

// Settings management
const loadSettings = () => {
  const saved = localStorage.getItem('readingSettings');
  if (saved) {
    const parsed = JSON.parse(saved);
    settings.fontSize = parsed.fontSize || 18;
    settings.themeName = parsed.themeName || 'light';
    settings.customColorEnabled = parsed.customColorEnabled || false;
    settings.customContentBg = parsed.customContentBg || '#FFFFFF';
    settings.customTextColor = parsed.customTextColor || '#111827';
    settings.textOutlineEnabled = parsed.textOutlineEnabled || false;
    settings.textOutlineColor = parsed.textOutlineColor || '#000000';
    
    const theme = colorThemes[parsed.themeName as keyof typeof colorThemes] || colorThemes.light;
    settings.bgColor = theme.bg;
    settings.fontColor = theme.font;
  }
  
  // Save reading mode preference
  localStorage.setItem('preferredReadingMode', 'flip');
};

const saveSettings = () => {
  localStorage.setItem('readingSettings', JSON.stringify({
    fontSize: settings.fontSize,
    themeName: settings.themeName,
    customColorEnabled: settings.customColorEnabled,
    customContentBg: settings.customContentBg,
    customTextColor: settings.customTextColor,
    textOutlineEnabled: settings.textOutlineEnabled,
    textOutlineColor: settings.textOutlineColor,
  }));
  
  nextTick(() => {
    // Re-calculate layout when settings change
    setTimeout(updateLayout, 100);
    updateDocumentBackground();
  });
};

const changeFontSize = (delta: number) => {
  const newSize = settings.fontSize + delta;
  if (newSize >= 12 && newSize <= 30) {
    settings.fontSize = newSize;
    saveSettings();
  }
};

const changeBgColor = (themeName: string) => {
  const theme = colorThemes[themeName as keyof typeof colorThemes];
  if (theme) {
    settings.themeName = themeName;
    settings.bgColor = theme.bg;
    settings.fontColor = theme.font;
    
    // Handle dark mode for dark themes (including AMOLED)
    const isDarkTheme = themeName === 'dark' || themeName === 'gray' || themeName === 'amoled';
    if (isDarkTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    
    saveSettings();
  }
};

// Helper function for theme names
const getThemeName = (name: string): string => {
  const names: Record<string, string> = {
    light: '白色',
    sepia: '泛黃',
    gray: '灰色',
    dark: '深黑',
    amoled: 'AMOLED 純黑',
  };
  return names[name] || name;
};

// Initialize custom colors from current theme if needed
const initializeCustomColorsFromTheme = () => {
  const theme = colorThemes[settings.themeName as keyof typeof colorThemes];
  if (theme) {
    settings.customContentBg = theme.bg;
    settings.customTextColor = theme.font;
  }
};

const resetCustomColors = () => {
  initializeCustomColorsFromTheme();
  if (settings.themeName === 'light') {
    settings.customContentBg = '#FFFFFF';
    settings.customTextColor = '#111827';
    settings.textOutlineColor = '#000000';
  }
  settings.textOutlineEnabled = false;
  saveSettings();
};

// Document background and navbar hiding
const updateDocumentBackground = () => {
  document.documentElement.style.backgroundColor = effectivePageBg.value;
  document.body.style.backgroundColor = effectivePageBg.value;
  document.body.classList.add('flip-reading-mode');
  
  if (settings.themeName === 'amoled') {
    document.documentElement.classList.add('reading-amoled');
  } else {
    document.documentElement.classList.remove('reading-amoled');
  }
};

const restoreDocumentBackground = () => {
  document.documentElement.style.backgroundColor = '';
  document.body.style.backgroundColor = '';
  document.body.classList.remove('flip-reading-mode');
  document.documentElement.classList.remove('reading-amoled');
};

// Fetch chapter
const fetchChapter = async () => {
  isLoading.value = true;
  error.value = null;
  currentPage.value = 1;
  layoutReady.value = false; // Hide content until layout is calculated
  
  try {
    const response = await apiClient.get<ChapterContent>(`/novels/${props.novelId}/chapters/${props.chapterId}/`);
    chapter.value = response.data;
    
    // Wait for content to render, then calculate layout
    await nextTick();
    setTimeout(() => {
      updateLayout();
      // Restore saved page progress after layout is calculated
      // Need another nextTick because updateLayout uses nextTick internally
      setTimeout(() => {
        restorePageProgress();
      }, 100);
    }, 200);
  } catch (err) {
    error.value = '無法載入章節內容。';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

// Lifecycle
onMounted(() => {
  loadSettings();
  updateDocumentBackground();
  fetchChapter();
  
  // Recalculate on resize
  window.addEventListener('resize', updateLayout);
});

onUnmounted(() => {
  restoreDocumentBackground();
  window.removeEventListener('resize', updateLayout);
});

// Watchers
watch(effectivePageBg, () => {
  updateDocumentBackground();
});

watch(() => props.chapterId, (newId, oldId) => {
  if (newId !== oldId) {
    fetchChapter();
  }
});

// Re-calculate when settings panel is closed (might affect width)
watch(showSettings, (newVal, oldVal) => {
  if (!newVal && oldVal) {
    setTimeout(updateLayout, 100);
  }
});
</script>

<style scoped>
.flip-reading-view {
  min-height: 100vh;
  min-height: 100dvh;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  touch-action: pan-y;
  -webkit-tap-highlight-color: transparent;
  /* Support for iPhone notch and home indicator */
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
  box-sizing: border-box;
}

/* Hide scrollbars */
.flip-reading-view,
.prose,
.column-container {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.flip-reading-view::-webkit-scrollbar,
.prose::-webkit-scrollbar,
.column-container::-webkit-scrollbar {
  display: none;
}

/* Column container styles */
.column-container {
  column-fill: auto !important;
  overflow: visible;
}

/* Prevent images from being cut across columns */
.prose :deep(img) {
  max-width: 100%;
  height: auto;
  break-inside: avoid;
  page-break-inside: avoid;
}

/* Paragraph styles */
.prose :deep(p) {
  text-align: justify;
  margin-bottom: 1em;
  orphans: 2;
  widows: 2;
  break-inside: avoid-column;
}

.prose :deep(p:empty) {
  min-height: 1em;
}

/* Manual page break markers - HIGHEST PRIORITY */
.prose :deep(hr[data-type="page-break"]),
.prose :deep(hr.page-break-marker) {
  display: block;
  visibility: hidden;
  height: 0;
  margin: 0;
  padding: 0;
  border: none;
  /* Force a column break AFTER this element (content after it starts in new column) */
  break-after: column;
  page-break-after: always;
  -webkit-column-break-after: always;
}

/* Toggle switches */
.toggle-switch {
  @apply relative inline-flex h-6 w-10 items-center rounded-full transition-colors;
}

.toggle-knob {
  @apply inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow;
}

.toggle-switch-sm {
  @apply relative inline-flex h-5 w-8 items-center rounded-full transition-colors;
}

.toggle-knob-sm {
  @apply inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow;
}

/* Setting items */
.setting-item {
  @apply flex items-center justify-between py-3;
}

.label {
  @apply text-sm font-medium text-gray-700 dark:text-gray-300;
}

.control {
  @apply flex items-center gap-2;
}

.btn-setting {
  @apply w-9 h-9 rounded-full flex items-center justify-center font-bold;
  @apply bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500;
}

/* Fade transition for overlays */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
