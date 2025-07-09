<!-- src/views/RegisterView.vue -->
<template>
  <div class="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-lg">
      <div>
        <h2 class="text-3xl font-extrabold text-center text-gray-900 dark:text-white">
          建立一個新帳號
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <!-- 輸入區塊 -->
        <div class="rounded-md shadow-sm">
          <div class="mb-4">
            <label for="username" class="sr-only">使用者名稱</label>
            <input 
              v-model="username" 
              id="username" 
              name="username" 
              type="text" 
              autocomplete="username" 
              required 
              class="form-input-field rounded-md" 
              placeholder="使用者名稱 (3-15字元)"
            >
          </div>
          <div class="mb-4">
            <label for="email" class="sr-only">電子郵件</label>
            <input 
              v-model="email" 
              id="email" 
              name="email" 
              type="email" 
              autocomplete="email" 
              required 
              class="form-input-field rounded-md" 
              placeholder="電子郵件"
            >
          </div>
          <div class="mb-4">
            <label for="password" class="sr-only">密碼</label>
            <input 
              v-model="password" 
              id="password" 
              name="password" 
              type="password" 
              autocomplete="new-password" 
              required 
              class="form-input-field rounded-md" 
              placeholder="密碼"
            >
          </div>
          <div>
            <label for="password2" class="sr-only">確認密碼</label>
            <input 
              v-model="password2" 
              id="password2" 
              name="password2" 
              type="password" 
              autocomplete="new-password" 
              required 
              class="form-input-field rounded-md" 
              placeholder="確認密碼"
            >
          </div>
        </div>
        
        <!-- 錯誤訊息 -->
        <p v-if="errorMsg" class="text-center text-red-500 text-sm h-4">
          {{ errorMsg }}
        </p>

        <!-- 註冊按鈕 -->
        <div>
          <button type="submit" :disabled="isLoading" class="group form-submit-button" :class="{ 'cursor-not-allowed opacity-75': isLoading }">
            <span v-if="!isLoading">註冊</span>
            <span v-else>處理中...</span>
          </button>
        </div>

        <!-- 切換至登入頁 -->
        <div class="text-center text-sm">
          <span class="text-gray-600 dark:text-gray-400">已經有帳號了？ </span>
          <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
            前往登入
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/axios';

const username = ref('');
const email = ref('');
const password = ref('');
const password2 = ref('');
const errorMsg = ref<string | null>(null);
const isLoading = ref(false);

const router = useRouter();

const handleRegister = async () => {
  if (isLoading.value) return;

  // 基本的前端驗證
  if (password.value !== password2.value) {
    errorMsg.value = "兩次輸入的密碼不一致！";
    return;
  }
  
  isLoading.value = true;
  errorMsg.value = null;
  
  try {
    await apiClient.post('/auth/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      password2: password2.value,
    });
    
    // 註冊成功後，可以給使用者一個提示，然後跳轉到登入頁面
    // 這裡我們直接跳轉
    router.push({ name: 'Login', query: { registered: 'true' } });
    
  } catch (error: any) {
    // 處理後端回傳的錯誤，例如使用者名稱已存在
    if (error.response?.data) {
      const errors = error.response.data;
      if (errors.username) {
        errorMsg.value = `使用者名稱: ${errors.username[0]}`;
      } else if (errors.email) {
        errorMsg.value = `電子郵件: ${errors.email[0]}`;
      } else {
        errorMsg.value = '註冊失敗，請檢查輸入的資料。';
      }
    } else {
      errorMsg.value = '發生未知錯誤，請稍後再試。';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>