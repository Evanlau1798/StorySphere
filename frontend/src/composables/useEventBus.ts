import { ref } from 'vue';

export enum EventType {
  ShowAlert = 'showAlert',
  ThemeChanged = 'theme-changed',
  Unauthorized = 'unauthorized',
}

type EventHandler = (payload?: any) => void;

const events = ref<Record<EventType, EventHandler[]>>({} as Record<EventType, EventHandler[]>);

export const eventBus = {
  on(event: EventType, callback: EventHandler) {
    if (!events.value[event]) {
      events.value[event] = [];
    }
    events.value[event].push(callback);
  },
  off(event: EventType, callback: EventHandler) {
    if (events.value[event]) {
      const index = events.value[event].indexOf(callback);
      if (index > -1) {
        events.value[event].splice(index, 1);
      }
    }
  },
  emit(event: EventType, payload?: any) {
    if (events.value[event]) {
      events.value[event].forEach((callback) => {
        callback(payload);
      });
    }
  },
};
