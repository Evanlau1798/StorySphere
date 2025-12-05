<!-- src/components/AppLayout.vue -->
<template>
  <div class="min-h-screen flex flex-col font-sans bg-gray-50 dark:bg-gray-900">
    <!-- 導覽列 -->
    <header class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-md sticky top-0 z-50">
      <nav class="container mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        <!-- Logo & 站名 -->
        <router-link to="/" class="text-2xl font-bold text-gray-800 dark:text-white transition-colors hover:text-blue-500">
          小說天地
        </router-link>

        <!-- 中間導覽連結 (桌面版) -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link to="/explore" class="nav-link">探索</router-link>
          <router-link to="/leaderboard" class="nav-link">排行榜</router-link>
          <router-link to="/updates" class="nav-link">最新更新</router-link>
          <router-link v-if="authStore.isAuthenticated" to="/recent" class="nav-link">最近瀏覽</router-link>
          <router-link v-if="authStore.isAuthenticated" to="/bookshelf" class="nav-link">我的書架</router-link>
        </div>

        <!-- 右側功能區 -->
        <div class="flex items-center space-x-2">
          <!-- 黑暗模式切換按鈕 (閱讀頁面隱藏) -->
          <button 
            v-if="route.name !== 'Reading'"
            @click="toggleDarkMode" 
            aria-label="切換顏色模式" 
            class="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <svg v-if="!isDarkMode" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
          </button>

          <!-- 手機版：我的書架 -->
          <router-link v-if="authStore.isAuthenticated" to="/bookshelf" class="md:hidden nav-link p-2">我的書架</router-link>

          <!-- 登入按鈕 (未登入時) -->
          <router-link v-if="!authStore.isAuthenticated" to="/login" class="login-button">登入</router-link>

          <!-- 手機版漢堡選單 / 桌面版使用者選單 -->
          <div v-if="authStore.isAuthenticated" class="relative" ref="userMenu">
            <button @click="toggleUserMenu" class="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <!-- 下拉式選單 -->
            <Transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div v-if="isUserMenuOpen" class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                  <!-- 讀者區 (手機版) -->
                  <div class="md:hidden">
                    <p class="dropdown-header">讀者區</p>
                    <router-link to="/explore" class="dropdown-item" @click="closeUserMenu">探索</router-link>
                    <router-link to="/leaderboard" class="dropdown-item" @click="closeUserMenu">排行榜</router-link>
                    <router-link to="/updates" class="dropdown-item" @click="closeUserMenu">最新更新</router-link>
                    <router-link to="/recent" class="dropdown-item" @click="closeUserMenu">最近瀏覽</router-link>
                    <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  </div>

                  <!-- 管理員區 -->
                  <div v-if="isAdmin">
                    <p class="dropdown-header">管理專區</p>
                    <router-link to="/admin" class="dropdown-item" @click="closeUserMenu">管理員後台</router-link>
                    <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  </div>

                  <!-- 作者區 -->
                  <!-- 作者區 -->
                  <div v-if="isAuthor">
                    <p class="dropdown-header">作者區</p>
                    <router-link to="/dashboard/novels" class="dropdown-item" @click="closeUserMenu">我的小說</router-link>
                    <router-link to="/dashboard/analytics" class="dropdown-item" @click="closeUserMenu">流量分析</router-link>
                    <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  </div>

                  <!-- 個人化 -->
                  <p class="dropdown-header">個人化</p>
                  <router-link to="/settings/profile" class="dropdown-item" @click="closeUserMenu">個人設定</router-link>
                  <button @click="handleLogout" class="dropdown-item-danger">登出</button>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </nav>
    </header>

    <!-- 主要內容區域 -->
    <main class="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <!-- 頁腳 -->
    <footer class="py-6 mt-12">
      <div class="container mx-auto text-center text-gray-500 dark:text-gray-400 text-sm">
        © {{ new Date().getFullYear() }} 小說天地. All Rights Reserved.
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { eventBus, EventType } from '../composables/useEventBus';

const { on } = eventBus;
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const userMenu = ref<HTMLElement | null>(null);
const isUserMenuOpen = ref(false);
const isDarkMode = ref(document.documentElement.classList.contains('dark'));

const isAuthor = computed(() => authStore.isAuthenticated && authStore.user?.role === 'AUTHOR');
const isAdmin = computed(() => authStore.isAuthenticated && authStore.user?.role === 'ADMIN');

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value;
};

const closeUserMenu = () => {
  isUserMenuOpen.value = false;
};

router.afterEach(() => {
  closeUserMenu();
});

const toggleDarkMode = () => {
  const newIsDark = !isDarkMode.value;
  isDarkMode.value = newIsDark;
  if (newIsDark) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
};

const handleLogout = () => {
  if (window.confirm('您確定要登出嗎？')) {
    authStore.logout();
    router.push('/');
    closeUserMenu();
  }
};

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true;
    document.documentElement.classList.add('dark');
  }

  on(EventType.ThemeChanged, (theme) => {
    isDarkMode.value = theme === 'dark';
  });

  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

const handleClickOutside = (event: MouseEvent) => {
  if (userMenu.value && !userMenu.value.contains(event.target as Node)) {
    closeUserMenu();
  }
};
</script>

<style scoped>
/* Component-specific styles can go here if needed */
</style>
