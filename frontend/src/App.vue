<template>
  <AppLayout />
  <GlobalAlert
    v-if="alert.visible"
    :type="alert.type"
    :title="alert.title"
    :message="alert.message"
    @close="closeAlert"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import AppLayout from './components/AppLayout.vue';
import GlobalAlert from './components/GlobalAlert.vue';
import { eventBus,EventType } from './composables/useEventBus';

type AlertType = 'success' | 'error' | 'warning' | 'info';

const alert = ref({
  visible: false,
  type: 'info' as AlertType,
  title: '',
  message: '',
});

const showAlert = (payload: { type: AlertType; title: string; message: string }) => {
  alert.value = { ...payload, visible: true };
  setTimeout(() => {
    closeAlert();
  }, 3000);
};

const closeAlert = () => {
  alert.value.visible = false;
};

onMounted(() => {
  eventBus.on(EventType.ShowAlert, showAlert);
});

onUnmounted(() => {
  eventBus.off(EventType.ShowAlert, showAlert);
});
</script>
