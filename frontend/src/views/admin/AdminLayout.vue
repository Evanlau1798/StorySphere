<template>
  <div class="flex flex-col md:flex-row h-full">
    <!-- Sidebar -->
    <aside class="w-full md:w-64 bg-white dark:bg-gray-800 shadow-md rounded-lg mb-6 md:mb-0 md:mr-6 flex-shrink-0">
      <div class="p-4 border-b border-gray-100 dark:border-gray-700">
        <h2 class="text-lg font-bold text-gray-800 dark:text-white">超級管理員後台</h2>
      </div>
      <nav class="p-2 space-y-1">
        <router-link to="/admin" exact-active-class="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400" class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          系統概覽
        </router-link>
        <router-link to="/admin/users" active-class="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400" class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
          使用者管理
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 min-h-[500px]">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
// Admin Layout
</script>
