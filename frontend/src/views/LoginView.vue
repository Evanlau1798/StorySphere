<!-- src/views/LoginView.vue -->
<template>
  <div class="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-lg">
      <div>
        <h2 class="text-3xl font-extrabold text-center text-gray-900 dark:text-white">
          登入您的帳號
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <!-- 輸入區塊 -->
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">使用者名稱</label>
            <input 
              v-model="username" 
              id="username" 
              name="username" 
              type="text" 
              autocomplete="username" 
              required 
              class="form-input-field rounded-t-md" 
              placeholder="使用者名稱"
            >
          </div>
          <div>
            <label for="password" class="sr-only">密碼</label>
            <input 
              v-model="password" 
              id="password" 
              name="password" 
              type="password" 
              autocomplete="current-password" 
              required 
              class="form-input-field rounded-b-md" 
              placeholder="密碼"
            >
          </div>
        </div>
        
        <!-- 額外選項：記住我 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input v-model="rememberMe" id="remember-me" name="remember-me" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600">
            <label for="remember-me" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">
              保持登入
            </label>
          </div>

          <div class="text-sm">
            <a href="#" class="font-medium text-blue-600 hover:text-blue-500">
              忘記密碼？
            </a>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <p v-if="errorMsg" class="text-center text-red-500 text-sm h-4">
          {{ errorMsg }}
        </p>

        <!-- 登入按鈕 -->
        <div>
          <button type="submit" :disabled="isLoading" class="group form-submit-button" :class="{ 'cursor-not-allowed opacity-75': isLoading }">
            <span v-if="!isLoading">登入</span>
            <span v-else>登入中...</span>
          </button>
        </div>

        <!-- 切換至註冊頁 -->
        <div class="text-center text-sm">
          <span class="text-gray-600 dark:text-gray-400">還沒有帳號嗎？ </span>
          <router-link to="/register" class="font-medium text-blue-600 hover:text-blue-500">
            立即註冊
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import apiClient from '../api/axios';

const username = ref('');
const password = ref('');
const rememberMe = ref(false); // 新增 rememberMe 狀態
const errorMsg = ref<string | null>(null);
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  if (isLoading.value) return;

  isLoading.value = true;
  errorMsg.value = null;

  try {
    const response = await apiClient.post('/auth/token/', {
      username: username.value,
      password: password.value,
      remember_me: rememberMe.value, // 傳遞 remember_me 參數
    });
    
    const { access, refresh } = response.data;
    authStore.setTokens(access, refresh);
    
    // 登入成功後跳轉到首頁
    router.push('/');
  } catch (error) {
    errorMsg.value = "登入失敗，請檢查帳號或密碼。";
    // 清除密碼欄位
    password.value = '';
  } finally {
    isLoading.value = false;
  }
};
</script>