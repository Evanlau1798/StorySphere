<!-- src/components/Modal.vue -->
<template>
  <transition name="modal-fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60" @click.self="close">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl overflow-hidden w-full max-w-lg mx-4" @click.stop>
        <div class="flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
            <slot name="header">Modal Title</slot>
          </h3>
          <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        <div class="p-6">
          <slot name="body">Modal Body</slot>
        </div>
        <div v-if="hasFooterSlot" class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 flex justify-end space-x-3">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { useSlots, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close']);

const slots = useSlots();
const hasFooterSlot = !!slots.footer;

const close = () => {
  emit('close');
};

const handleEsc = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.show) {
    close();
  }
};

watch(() => props.show, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
}, { immediate: true });

onMounted(() => {
  document.addEventListener('keydown', handleEsc);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEsc);
  document.body.style.overflow = ''; // Ensure scroll is re-enabled if component is unmounted
});
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
</style>