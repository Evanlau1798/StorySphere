<!-- src/views/ProfileSettingsView.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-white">個人資料設定</h1>

    <div v-if="isLoading" class="text-center py-10">載入中...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">{{ error }}</div>

    <form v-else-if="profile" @submit.prevent="updateProfile" class="max-w-2xl mx-auto bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
      
      <!-- 頭像上傳 -->
      <div class="flex items-center mb-8">
        <img :src="avatarPreview" class="w-24 h-24 rounded-full object-cover border-4 border-gray-200 dark:border-gray-700">
        <div class="ml-6">
          <label for="avatar-upload" class="cursor-pointer bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors">
            更換頭像
          </label>
          <input id="avatar-upload" type="file" @change="onFileChange" class="hidden" accept="image/*">
          <p class="text-xs text-gray-500 mt-2">支援 JPG, PNG, GIF. 檔案大小上限 2MB.</p>
        </div>
      </div>

      <!-- 使用者名稱 (不可修改) -->
      <div class="mb-6">
        <label class="block text-gray-700 dark:text-gray-300 font-bold mb-2">使用者名稱</label>
        <input 
          type="text" 
          :value="profile.username" 
          disabled
          class="w-full px-3 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-500 dark:text-gray-400"
        >
      </div>

      <!-- 作者專屬欄位 -->
      <div v-if="profile.role === 'AUTHOR'">
        <div class="mb-6">
          <label for="pen_name" class="block text-gray-700 dark:text-gray-300 font-bold mb-2">筆名</label>
          <input 
            id="pen_name"
            type="text" 
            v-model="editableProfile.pen_name"
            class="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>
        <div class="mb-6">
          <label for="bio" class="block text-gray-700 dark:text-gray-300 font-bold mb-2">個人簡介</label>
          <RichTextEditor v-model="editableProfile.bio" />
        </div>
      </div>
      
      <!-- 提交按鈕 -->
      <div class="mt-8 text-right">
        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="bg-green-500 text-white font-bold py-2 px-6 rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isSubmitting">儲存中...</span>
          <span v-else>儲存變更</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useAuthStore } from '../store/auth';
import apiClient from '../api/axios';
import RichTextEditor from '../components/RichTextEditor.vue';
import type { AuthorProfile } from '../types';
import { eventBus, EventType } from '../composables/useEventBus';

const profile = ref<AuthorProfile | null>(null);
const editableProfile = reactive({
  pen_name: '',
  bio: ''
});
const avatarFile = ref<File | null>(null);
const avatarPreview = ref<string>('https://via.placeholder.com/150.png/2d3748/ffffff?text=Avatar');

const isLoading = ref(true);
const isSubmitting = ref(false);
const error = ref<string | null>(null);

const authStore = useAuthStore();

const fetchProfile = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<AuthorProfile>('/profile/');
    profile.value = response.data;
    editableProfile.pen_name = response.data.pen_name || '';
    editableProfile.bio = response.data.bio || '';
    if (response.data.avatar) {
      avatarPreview.value = response.data.avatar;
    }
  } catch (err) {
    error.value = '無法載入個人資料。';
  } finally {
    isLoading.value = false;
  }
};

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    // 簡單的檔案大小驗證
    if (file.size > 2 * 1024 * 1024) {
      alert('檔案太大，請選擇小於 2MB 的圖片。');
      return;
    }
    avatarFile.value = file;
    // 建立本地預覽圖
    const reader = new FileReader();
    reader.onload = (event) => {
      avatarPreview.value = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

const updateProfile = async () => {
  if (!profile.value) return;

  isSubmitting.value = true;

  const formData = new FormData();
  
  // 只有在使用者是作者時才添加這些欄位
  if (profile.value.role === 'AUTHOR') {
    formData.append('pen_name', editableProfile.pen_name);
    formData.append('bio', editableProfile.bio);
  }

  if (avatarFile.value) {
    formData.append('avatar', avatarFile.value);
  }

  try {
    const response = await apiClient.patch<AuthorProfile>('/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // 更新 Pinia store 中的使用者資訊
    authStore.updateUser({
        avatar: response.data.avatar,
        pen_name: response.data.pen_name,
    });

    eventBus.emit(EventType.ShowAlert, {
      type: 'success',
      title: '成功',
      message: '個人資料更新成功！',
    });
    
    // 更新成功後，重設 avatarFile 以免重複上傳
    avatarFile.value = null;

  } catch (err) {
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '更新失敗，請稍後再試。',
    });
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(fetchProfile);
</script>