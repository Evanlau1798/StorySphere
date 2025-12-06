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
          <div class="mb-4 relative">
            <label for="password" class="sr-only">密碼</label>
            <input 
              v-model="password" 
              id="password" 
              name="password" 
              :type="showPassword ? 'text' : 'password'" 
              autocomplete="new-password" 
              required 
              class="form-input-field rounded-md pr-10" 
              placeholder="密碼"
            >
            <button 
              type="button" 
              @click="showPassword = !showPassword" 
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
            >
              <svg v-if="!showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
          <div class="relative">
            <label for="password2" class="sr-only">確認密碼</label>
            <input 
              v-model="password2" 
              id="password2" 
              name="password2" 
              :type="showConfirmPassword ? 'text' : 'password'" 
              autocomplete="new-password" 
              required 
              class="form-input-field rounded-md pr-10" 
              placeholder="確認密碼"
            >
            <button 
              type="button" 
              @click="showConfirmPassword = !showConfirmPassword" 
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
            >
              <svg v-if="!showConfirmPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
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
const showPassword = ref(false);
const showConfirmPassword = ref(false);
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