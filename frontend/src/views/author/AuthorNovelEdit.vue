<!-- src/views/author/AuthorNovelEdit.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="isLoading" class="text-center">載入中...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
    <div v-else>
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white">{{ isEditing ? '編輯小說' : '新增小說' }}</h1>
        <button @click="submitForm" class="btn-primary" :disabled="isSaving">
          {{ isSaving ? '儲存中...' : '儲存變更' }}
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column: Novel Details -->
        <div class="lg:col-span-1">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <form @submit.prevent="submitForm">
              <!-- Cover Image -->
              <div class="mb-6">
                <label class="block font-bold mb-2 text-gray-700 dark:text-gray-300">封面</label>
                <div class="w-full h-auto rounded-lg mb-2 flex items-center justify-center bg-gray-200 dark:bg-gray-700" style="min-height: 200px;">
                  <img v-if="coverPreview" :src="coverPreview" alt="Cover Preview" class="w-full h-auto rounded-lg object-cover">
                  <img v-else-if="novel.cover_image" :src="novel.cover_image" alt="Cover Preview" class="w-full h-auto rounded-lg object-cover">
                  <svg v-else class="w-24 h-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                </div>
                <input type="file" @change="handleCoverImageUpload" accept="image/*" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
              </div>

              <!-- Title -->
              <div class="mb-4">
                <label for="title" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">標題</label>
                <input type="text" id="title" v-model="novel.title" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600" />
              </div>

              <!-- Description -->
              <div class="mb-4">
                <label for="description" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">簡介</label>
                <textarea id="description" v-model="novel.description" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600" rows="8"></textarea>
              </div>

              <!-- Status -->
              <div class="mb-4">
                <label for="status" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">狀態</label>
                <select id="status" v-model="novel.status" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600">
                  <option value="ONGOING">連載中</option>
                  <option value="COMPLETED">已完結</option>
                  <option value="HIATUS">休刊中</option>
                </select>

              </div>

              <!-- Category -->
              <div class="mb-4">
                <label for="category" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">分類</label>
                <select id="category" v-model="novel.category" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600">
                  <option value="FANTASY">奇幻</option>
                  <option value="SCIFI">科幻</option>
                  <option value="ROMANCE">言情</option>
                  <option value="URBAN">都市</option>
                  <option value="HISTORY">歷史</option>
                  <option value="MARTIAL">武俠</option>
                  <option value="OTHERS">其他</option>
                </select>
              </div>
            </form>
          </div>
        </div>

        <!-- Right Column: Volumes and Chapters -->
        <div class="lg:col-span-2">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">分卷與章節管理</h2>

            <!-- Add New Volume -->
            <div class="mb-6 p-4 border rounded-lg bg-gray-50 dark:bg-gray-700">
              <h3 class="text-xl font-semibold mb-3 text-gray-800 dark:text-white">新增分卷</h3>
              <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                <input 
                  type="text" 
                  v-model="newVolumeTitle" 
                  placeholder="輸入分卷標題" 
                  class="flex-grow p-2 border rounded bg-gray-50 dark:bg-gray-800 dark:border-gray-600 text-gray-800 dark:text-gray-200"
                />
                <button @click="addVolume" class="btn-icon-label bg-blue-500 text-white" :disabled="!newVolumeTitle.trim() || isSaving">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                  <span class="hidden sm:inline">新增分卷</span>
                </button>
              </div>
            </div>

            <!-- Volumes List -->
            <div v-if="volumesLoading" class="text-center">載入分卷中...</div>
            <div v-else-if="volumes.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
              <p>尚未新增任何分卷。</p>
            </div>
            <div v-else class="space-y-4">
              <div v-for="volume in volumes" :key="volume.id" class="border rounded-lg overflow-hidden shadow-sm bg-gray-50 dark:bg-gray-700">
                <div class="flex justify-between items-center p-3 sm:p-4 bg-gray-100 dark:bg-gray-800">
                  <h3 class="text-base sm:text-lg font-semibold text-gray-800 dark:text-white truncate pr-2">{{ volume.title }} ({{ volume.chapters.length }} 章)</h3>
                  <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
                    <router-link :to="`/dashboard/novels/${novelId}/chapters/new?volumeId=${volume.id}`" class="btn-icon-label bg-green-500 text-white">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                      <span class="hidden sm:inline">新增</span>
                    </router-link>
                    <button @click="openEditVolumeModal(volume)" class="btn-icon-label bg-yellow-500 text-white">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
                      <span class="hidden sm:inline">編輯</span>
                    </button>
                    <button @click="deleteVolume(volume.id)" class="btn-icon-label bg-red-500 text-white">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" /></svg>
                      <span class="hidden sm:inline">刪除</span>
                    </button>
                  </div>
                </div>
                <ul class="divide-y divide-gray-200 dark:divide-gray-600">
                  <li v-for="chapter in volume.chapters" :key="chapter.id" class="flex justify-between items-center p-3 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                    <span class="text-gray-800 dark:text-gray-200 truncate pr-2">
                      {{ chapter.title }}
                      <span v-if="chapter.status === 'DRAFT'" class="text-xs text-yellow-500 ml-2"> (草稿)</span>
                    </span>
                    <div class="flex items-center space-x-2">
                      <router-link :to="`/dashboard/novels/${novelId}/chapters/${chapter.id}/edit`" class="btn-icon text-blue-500" title="編輯">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
                      </router-link>
                      <button @click="deleteChapter(chapter.id)" class="btn-icon text-red-500" title="刪除">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" /></svg>
                      </button>
                    </div>
                  </li>
                  <li v-if="volume.chapters.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-3">
                    此分卷下沒有章節。
                  </li>
                </ul>
              </div>
            </div>

            <!-- Chapters without Volume -->
            <div v-if="chaptersWithoutVolume.length > 0" class="mt-8 p-4 border rounded-lg bg-gray-50 dark:bg-gray-700">
              <h3 class="text-xl font-semibold mb-3 text-gray-800 dark:text-white">未分卷章節</h3>
              <ul class="divide-y divide-gray-200 dark:divide-gray-600">
                <li v-for="chapter in chaptersWithoutVolume" :key="chapter.id" class="flex justify-between items-center p-3 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                  <span class="text-gray-800 dark:text-gray-200 truncate pr-2">
                    {{ chapter.title }}
                    <span v-if="chapter.status === 'DRAFT'" class="text-xs text-yellow-500 ml-2"> (草稿)</span>
                  </span>
                  <div class="flex items-center space-x-2">
                    <router-link :to="`/dashboard/novels/${novelId}/chapters/${chapter.id}/edit`" class="btn-icon text-blue-500" title="編輯">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
                    </router-link>
                    <button @click="deleteChapter(chapter.id)" class="btn-icon text-red-500" title="刪除">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" /></svg>
                    </button>
                  </div>
                </li>
              </ul>
            </div>

            <div v-if="!volumesLoading && volumes.length === 0 && chaptersWithoutVolume.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
              <p>這本小說還沒有任何章節或分卷。</p>
              <router-link :to="`/dashboard/novels/${novelId}/chapters/new`" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-600 transition-colors">
                新增第一章
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Volume Modal -->
    <Modal :show="showEditVolumeModal" @close="showEditVolumeModal = false">
      <template #header>編輯分卷</template>
      <template #body>
        <div v-if="editingVolume">
          <form @submit.prevent="saveVolumeChanges">
            <!-- Volume Title -->
            <div class="mb-4">
              <label for="volumeTitle" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">分卷標題</label>
              <input type="text" id="volumeTitle" v-model="editingVolume.title" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600" />
            </div>

            <!-- Volume Description -->
            <div class="mb-4">
              <label for="volumeDescription" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">分卷簡介</label>
              <textarea id="volumeDescription" v-model="editingVolume.description" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600" rows="4"></textarea>
            </div>

            <!-- Volume Cover Image -->
            <div class="mb-6">
              <label class="block font-bold mb-2 text-gray-700 dark:text-gray-300">分卷封面</label>
              <div class="w-full h-auto rounded-lg mb-2 flex items-center justify-center bg-gray-200 dark:bg-gray-700" style="min-height: 150px;">
                <img v-if="volumeCoverPreview" :src="volumeCoverPreview" alt="Volume Cover Preview" class="w-full h-auto rounded-lg object-cover">
                <svg v-else class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
              </div>
              <input type="file" @change="handleVolumeCoverImageUpload" accept="image/*" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
          </form>
        </div>
      </template>
      <template #footer>
        <button @click="showEditVolumeModal = false" class="btn-secondary">取消</button>
        <button @click="saveVolumeChanges" class="btn-primary" :disabled="isSaving">{{ isSaving ? '儲存中...' : '儲存' }}</button>
      </template>
    </Modal>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../api/axios';
import type { Novel, Chapter, Volume } from '../../types';
import { eventBus, EventType } from '../../composables/useEventBus';
import Modal from '@/components/Modal.vue'; // Import Modal

const route = useRoute();
const router = useRouter();

const novelId = computed(() => route.params.novelId as string);
const isEditing = computed(() => !!novelId.value && novelId.value !== 'new');

const novel = ref<Partial<Novel>>({
  title: '',
  description: '',
  status: 'ONGOING',
  category: 'OTHERS',
  cover_image: null,
});
const volumes = ref<Volume[]>([]);
const newVolumeTitle = ref('');
const chapters = ref<Chapter[]>([]);
const coverImageFile = ref<File | null>(null);
const coverPreview = ref<string | null>(null);

const isLoading = ref(true);
const isSaving = ref(false);
const volumesLoading = ref(true);
const error = ref<string | null>(null);

// Modal states
const showEditVolumeModal = ref(false);
const editingVolume = ref<Partial<Volume> | null>(null);
const volumeCoverImageFile = ref<File | null>(null);
const volumeCoverPreview = ref<string | null>(null);


const chaptersWithoutVolume = computed(() => {
  return chapters.value.filter(chapter => !chapter.volume);
});

const fetchNovelData = async () => {
  if (!isEditing.value) {
    isLoading.value = false;
    volumesLoading.value = false;
    return;
  }
  try {
    isLoading.value = true;
    volumesLoading.value = true;
    const response = await apiClient.get<Novel>(`/novels/${novelId.value}/?view=edit`);
    const data = response.data;
    novel.value = data;
    volumes.value = data.volumes || [];
    chapters.value = data.chapters_without_volume || [];
  } catch (err) {
    console.error(err);
    error.value = "無法載入小說資料。";
  } finally {
    isLoading.value = false;
    volumesLoading.value = false;
  }
};

const handleCoverImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    coverImageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      coverPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

const submitForm = async () => {
  isSaving.value = true;
  const formData = new FormData();
  formData.append('title', novel.value.title || '');
  formData.append('description', novel.value.description || '');
  formData.append('status', novel.value.status || 'ONGOING');
  formData.append('category', novel.value.category || 'OTHERS');
  if (coverImageFile.value) {
    formData.append('cover_image', coverImageFile.value);
  }

  try {
    let response;
    if (isEditing.value) {
      response = await apiClient.patch(`/novels/${novelId.value}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '小說資訊已更新！',
      });
    } else {
      response = await apiClient.post('/novels/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '小說已成功建立！',
      });
      router.push(`/dashboard/novels/${response.data.id}/edit`);
    }
  } catch (err) {
    console.error('Failed to save novel', err);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '儲存失敗，請稍後再試。',
    });
  } finally {
    isSaving.value = false;
  }
};

const addVolume = async () => {
  if (!novelId.value || !newVolumeTitle.value.trim()) return;
  isSaving.value = true;
  try {
    const response = await apiClient.post(`/novels/${novelId.value}/volumes/`, {
      title: newVolumeTitle.value,
    });
    volumes.value.push({ ...response.data, chapters: [] });
    newVolumeTitle.value = '';
    eventBus.emit(EventType.ShowAlert, {
      type: 'success',
      title: '成功',
      message: '分卷已新增！',
    });
  } catch (error) {
    console.error('Failed to add volume', error);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '新增分卷失敗，請稍後再試。',
    });
  } finally {
    isSaving.value = false;
  }
};

const openEditVolumeModal = (volume: Volume) => {
  editingVolume.value = { ...volume }; // Create a copy to avoid direct mutation
  volumeCoverPreview.value = volume.cover_image || null;
  volumeCoverImageFile.value = null;
  showEditVolumeModal.value = true;
};

const handleVolumeCoverImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    volumeCoverImageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      volumeCoverPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

const saveVolumeChanges = async () => {
  if (!editingVolume.value || !editingVolume.value.id) return;
  isSaving.value = true;
  
  const formData = new FormData();
  formData.append('title', editingVolume.value.title || '');
  formData.append('description', editingVolume.value.description || '');
  if (volumeCoverImageFile.value) {
    formData.append('cover_image', volumeCoverImageFile.value);
  }

  try {
    const response = await apiClient.patch(`/novels/${novelId.value}/volumes/${editingVolume.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    const index = volumes.value.findIndex(v => v.id === editingVolume.value!.id);
    if (index !== -1) {
      // Preserve chapters, update other fields from response
      volumes.value[index] = { ...volumes.value[index], ...response.data };
    }
    
    showEditVolumeModal.value = false;
    eventBus.emit(EventType.ShowAlert, {
      type: 'success',
      title: '成功',
      message: '分卷已更新！',
    });
  } catch (error) {
    console.error('Failed to update volume', error);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '更新分卷失敗，請稍後再試。',
    });
  } finally {
    isSaving.value = false;
  }
};


const deleteVolume = async (volumeId: number) => {
  if (confirm('確定要刪除此分卷嗎？此操作將會把分卷下的章節移至未分卷章節。')) {
    isSaving.value = true;
    try {
      await apiClient.delete(`/novels/${novelId.value}/volumes/${volumeId}/`);
      volumes.value = volumes.value.filter(v => v.id !== volumeId);
      fetchNovelData(); 
      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '分卷已刪除！',
      });
    } catch (error) {
      console.error('Failed to delete volume', error);
      eventBus.emit(EventType.ShowAlert, {
        type: 'error',
        title: '錯誤',
        message: '刪除分卷失敗，請稍後再試。',
      });
    } finally {
      isSaving.value = false;
    }
  }
};

const deleteChapter = async (chapterId: number) => {
  if (confirm('確定要刪除此章節嗎？此操作無法復原。')) {
    isSaving.value = true;
    try {
      await apiClient.delete(`/novels/${novelId.value}/chapters/${chapterId}/`);
      
      for (const volume of volumes.value) {
        const index = volume.chapters.findIndex(c => c.id === chapterId);
        if (index !== -1) {
          volume.chapters.splice(index, 1);
          break;
        }
      }
      const index = chapters.value.findIndex(c => c.id === chapterId);
      if (index !== -1) {
        chapters.value.splice(index, 1);
      }

      eventBus.emit(EventType.ShowAlert, {
        type: 'success',
        title: '成功',
        message: '章節已刪除！',
      });
    } catch (error) {
      console.error('Failed to delete chapter', error);
      eventBus.emit(EventType.ShowAlert, {
        type: 'error',
        title: '錯誤',
        message: '刪除章節失敗，請稍後再試。',
      });
    } finally {
      isSaving.value = false;
    }
  }
};

onMounted(fetchNovelData);
</script>

<style scoped>
.btn-primary, .btn-secondary {
  @apply font-semibold py-2 px-4 rounded-lg shadow-md transition-transform transform hover:scale-105 disabled:opacity-50 text-center;
}
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white;
}
.btn-secondary {
  @apply bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
.btn-icon {
    @apply p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors;
}
.btn-icon-label {
    @apply flex items-center space-x-2 px-3 py-1.5 text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50;
}
</style>