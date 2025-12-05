<!-- src/views/author/AuthorChapterEdit.vue -->
<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">{{ isEditing ? '編輯章節' : '新增章節' }}</h1>
      <div class="flex items-center space-x-4">
        <span v-if="lastSaved" class="text-sm text-gray-500 dark:text-gray-400">
          最後儲存於: {{ lastSaved }}
        </span>
        <input type="file" ref="fileInput" @change="handleFileUpload" accept=".txt" class="hidden" />
        <button type="button" @click="publishChapter" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" :disabled="isSaving">{{ isSaving ? '發布中...' : '儲存並發布' }}</button>
      </div>
    </div>
    <form @submit.prevent="publishChapter">
      <div class="mb-4">
        <label for="title" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">章節標題</label>
        <input type="text" id="title" v-model="chapter.title" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600" />
      </div>
      <div class="mb-4">
        <label for="volume" class="block font-bold mb-1 text-gray-700 dark:text-gray-300">所屬分卷 (可選)</label>
        <select id="volume" v-model="selectedVolumeId" class="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 dark:border-gray-600">
          <option :value="null">無分卷</option>
          <option v-for="volume in volumes" :key="volume.id" :value="volume.id">{{ volume.title }}</option>
        </select>
      </div>
      <div class="mb-4">
        <label for="content" class="block font-bold mb-1">內容</label>
        <RichTextEditor v-model="chapter.content" />
      </div>
      <div class="flex justify-end items-center space-x-4 mt-4">
        <button v-if="isEditorEmpty" type="button" @click="triggerFileInput" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">從txt檔匯入</button>
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" :disabled="isSaving">{{ isSaving ? '發布中...' : '儲存並發布' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../api/axios';
import RichTextEditor from '../../components/RichTextEditor.vue';
import type { Chapter, Volume } from '../../types';
import { eventBus, EventType } from '../../composables/useEventBus';

const props = defineProps({ 
  novelId: { type: String, required: true },
  chapterId: { type: String }
});

const router = useRouter();
const isEditing = computed(() => !!props.chapterId);

const chapter = ref<Partial<Chapter> & { content?: string }>({ title: '', content: '', status: 'DRAFT' });
const fileInput = ref<HTMLInputElement | null>(null);
const volumes = ref<Volume[]>([]);
const selectedVolumeId = ref<number | null>(null);
const isSaving = ref(false);
const lastSaved = ref<string | null>(null);
let autoSaveTimer: number | null = null;

const isEditorEmpty = computed(() => {
  const content = chapter.value.content || '';
  const textOnly = content.replace(/<[^>]*>/g, '').trim();
  return textOnly.length === 0;
});

const fetchVolumes = async () => {
  try {
    const response = await apiClient.get(`/novels/${props.novelId}/volumes/`);
    volumes.value = response.data.results || response.data; // Handle both paginated and non-paginated responses
  } catch (error) {
    console.error('Failed to fetch volumes', error);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '無法載入分卷列表。',
    });
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      chapter.value.content = (e.target?.result as string).replace(/\n/g, '<br>');
    };
    reader.readAsText(file);
  }
};

const saveDraft = async () => {
  // If there's no title, don't save.
  if (!chapter.value.title?.trim()) return;

  isSaving.value = true;
  try {
    const payload: {
      title: string | undefined;
      content: string | undefined;
      volume: number | null;
      status?: 'DRAFT' | 'PUBLISHED';
    } = {
      title: chapter.value.title,
      content: chapter.value.content,
      volume: selectedVolumeId.value,
    };

    if (isEditing.value && chapter.value.status) {
      payload.status = chapter.value.status;
    } else {
      payload.status = 'DRAFT';
    }
    
    const currentChapterId = chapter.value.id || (isEditing.value ? props.chapterId : null);

    let response;
    if (currentChapterId) {
      response = await apiClient.patch(`/novels/${props.novelId}/chapters/${currentChapterId}/`, payload);
    } else {
      response = await apiClient.post(`/novels/${props.novelId}/chapters/`, payload);
      router.replace(`/dashboard/novels/${props.novelId}/chapters/${response.data.id}/edit`);
    }

    const updatedChapter = response.data;
    updatedChapter.content = updatedChapter.content || '';
    chapter.value = { ...chapter.value, ...updatedChapter };
    lastSaved.value = new Date().toLocaleTimeString();

  } catch (error) {
    console.error('Failed to save draft', error);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '草稿儲存失敗',
      message: '無法自動儲存草稿，請檢查網路連線。',
    });
  }
 finally {
    isSaving.value = false;
  }
};

const publishChapter = async () => {
  isSaving.value = true;
  try {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    await saveDraft();

    const payload = {
      title: chapter.value.title,
      content: chapter.value.content,
      volume: selectedVolumeId.value,
      status: 'PUBLISHED' as const,
    };

    const currentChapterId = chapter.value.id || (isEditing.value ? props.chapterId : null);

    if (currentChapterId) {
      await apiClient.patch(`/novels/${props.novelId}/chapters/${currentChapterId}/`, payload);
    } else {
      const response = await apiClient.post(`/novels/${props.novelId}/chapters/`, payload);
      chapter.value.id = response.data.id;
    }
    
    eventBus.emit(EventType.ShowAlert, {
      type: 'success',
      title: '成功',
      message: `章節已成功發布！`,
    });
    router.push(`/dashboard/novels/${props.novelId}/edit`);
  } catch (error) {
    console.error('Failed to publish chapter', error);
    eventBus.emit(EventType.ShowAlert, {
      type: 'error',
      title: '錯誤',
      message: '發布章節失敗，請稍後再試。',
    });
  } finally {
    isSaving.value = false;
  }
};

watch([() => chapter.value.title, () => chapter.value.content], () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer);
  }
  autoSaveTimer = window.setTimeout(() => {
    saveDraft();
  }, 5000);
});

onMounted(() => {
  const route = useRoute();
  fetchVolumes();
  if (isEditing.value && props.chapterId) {
    apiClient.get(`/novels/${props.novelId}/chapters/${props.chapterId}/`).then(response => {
      const fetchedChapter = response.data;
      // Ensure content is a string to prevent v-model errors
      fetchedChapter.content = fetchedChapter.content || '';
      chapter.value = fetchedChapter;
      selectedVolumeId.value = response.data.volume;
    });
  } else {
    const volumeIdFromQuery = route.query.volumeId;
    if (volumeIdFromQuery) {
      selectedVolumeId.value = Number(volumeIdFromQuery);
    }
  }
});

</script>