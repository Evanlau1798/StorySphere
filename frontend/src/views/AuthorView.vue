<!-- src/views/AuthorView.vue -->
<template>
  <div class="pt-8">
    <div v-if="isLoading" class="text-center py-20">載入作者資訊中...</div>
    <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>
    
    <div v-else-if="author" class="container mx-auto px-4">
      <!-- 作者資訊卡片 -->
      <div class="flex flex-col sm:flex-row items-center bg-white dark:bg-gray-800 p-6 sm:p-8 rounded-2xl shadow-lg">
        <img :src="authorAvatar" :alt="author.pen_name || author.username" class="w-32 h-32 sm:w-40 sm:h-40 rounded-full object-cover border-4 border-gray-200 dark:border-gray-700 shadow-md">
        <div class="mt-6 sm:mt-0 sm:ml-8 text-center sm:text-left">
          <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">{{ author.pen_name || author.username }}</h1>
          <p v-if="author.pen_name" class="text-md text-gray-500 dark:text-gray-400 mt-1">@{{ author.username }}</p>
          <p class="mt-4 text-gray-600 dark:text-gray-300 max-w-xl"><span v-html="author.bio"></span></p>
        </div>
      </div>

      <!-- 作者作品列表 -->
      <div class="mt-12">
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">TA 的作品 ({{ author.novels.length }})</h2>
        <div v-if="author.novels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <NovelCard v-for="novel in author.novels" :key="novel.id" :novel="novel" />
        </div>
        <div v-else class="text-center py-10 bg-white dark:bg-gray-800/50 rounded-lg shadow-sm">
          <p class="text-gray-500">這位作者還沒有發布任何作品。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '../api/axios';
import type { AuthorProfile, Novel, SimpleNovel } from '../types';
import NovelCard from '../components/NovelCard.vue';

const props = defineProps({ id: { type: String, required: true } });

// The author ref will hold the profile, but we ensure its 'novels' property is an array of full Novel objects.
const author = ref<(Omit<AuthorProfile, 'novels'> & { novels: Novel[] }) | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

const fetchAuthorProfile = async (authorId: string) => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<AuthorProfile>(`/users/author/${authorId}/`);
    const profileData = response.data;

    // The API returns SimpleNovel objects. We map them to full Novel objects
    // to satisfy the NovelCard component's prop requirements.
    const fullNovels: Novel[] = profileData.novels.map((simpleNovel: SimpleNovel) => ({
      ...simpleNovel,
      author: { // Add the author object to each novel
        user_id: profileData.user_id,
        username: profileData.username,
        pen_name: profileData.pen_name,
      },
      volumes: [], // Add missing volumes property
      created_at: '', // Add other missing properties to satisfy the Novel type
      chapters_without_volume: [],
    }));

    author.value = {
      ...profileData,
      novels: fullNovels,
    };

  } catch (err: any) {
    error.value = "無法載入作者資訊。";
  } finally {
    isLoading.value = false;
  }
};

const authorAvatar = computed(() => {
  if (author.value?.avatar) {
    return author.value.avatar;
  }
  // Provide a default placeholder image
  return 'https://via.placeholder.com/150.png/2d3748/ffffff?text=Avatar';
});

onMounted(() => { 
  if (props.id) {
    fetchAuthorProfile(props.id); 
  }
});

watch(() => props.id, (newId) => { 
  if (newId) {
    fetchAuthorProfile(newId); 
  }
});
</script>
