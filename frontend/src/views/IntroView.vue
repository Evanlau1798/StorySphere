<template>
  <div class="relative min-h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden font-sans selection:bg-indigo-500 selection:text-white">
    
    <!-- Background Decor (Gradient blobs) -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-purple-400/30 dark:bg-purple-900/40 blur-3xl animate-blob"></div>
      <div class="absolute top-[20%] -right-[10%] w-[40%] h-[40%] rounded-full bg-indigo-400/30 dark:bg-indigo-900/40 blur-3xl animate-blob animation-delay-2000"></div>
      <div class="absolute -bottom-[20%] left-[20%] w-[60%] h-[60%] rounded-full bg-blue-400/30 dark:bg-blue-900/40 blur-3xl animate-blob animation-delay-4000"></div>
    </div>

    <!-- Hero Section -->
    <div class="relative z-10 pt-20 pb-16 sm:pt-24 sm:pb-20 lg:pb-28 lg:pt-32">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center">
          <h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-6 drop-shadow-sm">
            <span class="block mb-2">探索無限的</span>
            <span class="block bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 animate-gradient-x">
              故事宇宙
            </span>
          </h1>
          <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-300 leading-relaxed">
            StorySphere 是一個專為小說愛好者打造的現代化閱讀平台。<br class="hidden sm:block" />
            在這裡，發現原創故事，建立專屬書架，與創作者一同成長。
          </p>
          <div class="mt-10 flex justify-center gap-4">
            <router-link 
              to="/explore" 
              class="px-8 py-3.5 rounded-full bg-indigo-600 text-white font-semibold text-lg hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-500/30 transform hover:-translate-y-1"
            >
              開始閱讀
            </router-link>
            <router-link 
              to="/register" 
              class="px-8 py-3.5 rounded-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold text-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all shadow-sm hover:shadow-md transform hover:-translate-y-1"
            >
              註冊帳號
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="relative z-10 py-16 sm:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-base font-semibold text-indigo-600 dark:text-indigo-400 tracking-wide uppercase">平台特色</h2>
          <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
            打造極致的閱讀體驗
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div v-for="(feature, index) in features" :key="index" class="relative group">
            <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-100 transition duration-500 group-hover:duration-200"></div>
            <div class="relative p-6 bg-white dark:bg-gray-800 rounded-xl shadow-xl h-full flex flex-col items-center text-center transition-transform duration-300 group-hover:-translate-y-1">
              <div class="h-12 w-12 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4 group-hover:scale-110 transition-transform duration-300">
                <component :is="feature.icon" class="h-6 w-6" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ feature.name }}</h3>
              <p class="text-gray-500 dark:text-gray-400 leading-relaxed">{{ feature.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="relative z-10 py-16">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="relative p-8 sm:p-12 bg-indigo-600 rounded-3xl overflow-hidden shadow-2xl">
          <div class="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
          <div class="absolute bottom-0 left-0 -mb-10 -ml-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
          
          <h2 class="text-2xl sm:text-3xl font-bold text-white mb-4">準備好開始您的旅程了嗎？</h2>
          <p class="text-indigo-100 text-lg mb-8 max-w-2xl mx-auto">
            加入 StorySphere，探索成千上萬個精彩世界，或是動筆寫下屬於您的傳奇。
          </p>
          <router-link to="/explore" class="inline-block px-8 py-3 bg-white text-indigo-600 font-bold rounded-full shadow-lg hover:bg-gray-50 transition-colors transform hover:scale-105 active:scale-95">
            立即探索
          </router-link>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';

// Inline Icons (Same as before, simplified for this snippet)
const BookOpenIcon = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': 2 }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
  ])
};

const SparklesIcon = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': 2 }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' })
  ])
};

const DevicePhoneMobileIcon = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': 2 }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z' })
  ])
};

const UserGroupIcon = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': 2 }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' })
  ])
};

const features = [
  {
    name: '豐富的藏書',
    description: '匯集各類原創小說，從奇幻冒險到現代都市，滿足不同的閱讀口味。',
    icon: BookOpenIcon,
  },
  {
    name: '簡潔的介面',
    description: '專注於閱讀的設計，支援深色模式，保護您的舒適閱讀時光。',
    icon: DevicePhoneMobileIcon,
  },
  {
    name: '即時更新互動',
    description: '關注您喜愛的作者，第一時間收到章節更新通知，並參與評論互動。',
    icon: UserGroupIcon,
  },
  {
    name: '創作您的世界',
    description: '提供完善的作者後台，輕鬆管理作品與章節，實現您的作家夢。',
    icon: SparklesIcon,
  },
];
</script>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

@keyframes gradient-x {
  0%, 100% {
    background-size: 200% 200%;
    background-position: left center;
  }
  50% {
    background-size: 200% 200%;
    background-position: right center;
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-gradient-x {
  animation: gradient-x 3s ease infinite;
}
</style>
