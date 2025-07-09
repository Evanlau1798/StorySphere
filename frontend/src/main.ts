// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import axios from './api/axios' // 引入 axios 實例

const app = createApp(App)

// 全域錯誤處理器
app.config.errorHandler = (err, instance, info) => {
  console.error("Caught in global handler:", err, instance, info);

  // 從錯誤物件中提取訊息和堆疊
  const message = err instanceof Error ? err.message : String(err);
  const stack = err instanceof Error ? err.stack : 'N/A';

  // 準備要發送到後端的資料
  const errorData = {
    message: `[${info}] ${message}`,
    stack: stack,
    // 你可以加入更多環境資訊
    // location: window.location.href,
    // userAgent: navigator.userAgent,
  };

  // 發送到後端
  axios.post('/api/log-frontend-error/', errorData)
    .catch(loggingError => {
      console.error("Failed to send error log to backend:", loggingError);
    });
};


app.use(createPinia())
app.use(router)

app.mount('#app')