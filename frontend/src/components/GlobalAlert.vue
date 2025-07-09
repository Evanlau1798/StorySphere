<template>
  <div v-if="visible" :class="containerClasses">
    <div class="flex items-center">
      <span class="font-semibold">{{ title }}</span>
    </div>
    <p class="text-sm">{{ message }}</p>
    <button @click="close" class="absolute top-0 right-0 mt-2 mr-2 text-lg font-bold">&times;</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

interface Props {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000,
});

const visible = ref(true);

const containerClasses = computed(() => [
  'fixed',
  'top-5',
  'right-5',
  'p-4',
  'rounded-lg',
  'shadow-lg',
  'z-50',
  'max-w-sm',
  {
    'bg-green-100': props.type === 'success',
    'border-green-400': props.type === 'success',
    'text-green-700': props.type === 'success',
    'bg-red-100': props.type === 'error',
    'border-red-400': props.type === 'error',
    'text-red-700': props.type === 'error',
    'bg-yellow-100': props.type === 'warning',
    'border-yellow-400': props.type === 'warning',
    'text-yellow-700': props.type === 'warning',
    'bg-blue-100': props.type === 'info',
    'border-blue-400': props.type === 'info',
    'text-blue-700': props.type === 'info',
  },
]);

const close = () => {
  visible.value = false;
};

watch(
  () => props.duration,
  (newDuration) => {
    if (newDuration) {
      setTimeout(close, newDuration);
    }
  },
  { immediate: true }
);
</script>
