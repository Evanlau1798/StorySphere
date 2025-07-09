import axios from 'axios';
import { useAuthStore } from '../store/auth';

const apiClient = axios.create({
    baseURL: '/api', 
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Adds the Authorization header to every request
apiClient.interceptors.request.use(config => {
    const authStore = useAuthStore();
    const accessToken = authStore.accessToken;
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// --- Advanced Response Interceptor with Token Refresh Logic ---

let isRefreshing = false;
let failedQueue: { resolve: (value: unknown) => void, reject: (reason?: any) => void }[] = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

apiClient.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        const authStore = useAuthStore();

        // Only handle 401 errors, and ensure it's not a retry or a refresh token request itself
        if (error.response.status === 401 && !originalRequest._retry) {
            
            if (isRefreshing) {
                // If a refresh is already in progress, queue the original request
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers['Authorization'] = 'Bearer ' + token;
                    return apiClient(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const refreshToken = authStore.refreshToken;
                if (!refreshToken) {
                    // If no refresh token, logout immediately
                    authStore.logout();
                    return Promise.reject(error);
                }

                // Request a new access token using the refresh token
                const { data } = await axios.post('/api/auth/token/refresh/', {
                    refresh: refreshToken
                });

                const newAccessToken = data.access;
                authStore.setAccessToken(newAccessToken); // Update the store with the new token

                // Update the header of the original request and process the queue
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                processQueue(null, newAccessToken);
                
                // Retry the original request with the new token
                return apiClient(originalRequest);

            } catch (refreshError) {
                // If the refresh token is invalid, logout the user
                processQueue(refreshError, null);
                authStore.logout();
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;
