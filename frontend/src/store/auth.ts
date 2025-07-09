import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { jwtDecode } from 'jwt-decode';
import { eventBus, EventType } from '../composables/useEventBus';
import { useRouter } from 'vue-router';

// 定義使用者資訊的介面
interface User {
  user_id: number;
  username: string;
  role: 'READER' | 'AUTHOR';
  avatar: string | null;
  pen_name: string | null;
}

export const useAuthStore = defineStore('auth', () => {
    const router = useRouter();
    // 從 localStorage 初始化 state
    const accessToken = ref<string | null>(localStorage.getItem('accessToken'));
    const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'));
    // Initialize user to null, it will be populated from JWT if accessToken exists
    const user = ref<User | null>(null); // CHANGE HERE

    const isAuthenticated = computed(() => !!accessToken.value && !!user.value);
    const isAuthor = computed(() => user.value?.role === 'AUTHOR');

    // 解析 JWT 並儲存使用者資訊
    function decodeAndStoreUser(token: string) {
        try {
            const decoded = jwtDecode<User>(token);
            const userData = {
                user_id: decoded.user_id,
                username: decoded.username,
                role: decoded.role,
                avatar: decoded.avatar,
                pen_name: decoded.pen_name,
            };
            user.value = userData;
            localStorage.setItem('user', JSON.stringify(userData));
        } catch (error) {
            console.error('Failed to decode token or store user:', error);
            // 如果解碼失敗，清除舊的登入狀態
            logout();
        }
    }

    function setTokens(access: string, refresh: string) {
        accessToken.value = access;
        refreshToken.value = refresh;
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);
        // 登入時，解析新的 access token
        decodeAndStoreUser(access);
    }

    function setAccessToken(access: string) {
        accessToken.value = access;
        localStorage.setItem('accessToken', access);
        decodeAndStoreUser(access);
    }

    function logout() {
        accessToken.value = null;
        refreshToken.value = null;
        user.value = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        router.push('/login'); // Redirect to login page on logout
    }

    // 更新使用者部分資訊 (例如頭像、筆名)
    function updateUser(payload: Partial<Pick<User, 'avatar' | 'pen_name'>>) {
        if (user.value) {
            const updatedUser = { ...user.value, ...payload };
            user.value = updatedUser;
            localStorage.setItem('user', JSON.stringify(updatedUser));
        }
    }

    function checkAuth() {
        const token = localStorage.getItem('accessToken');
        if (token) {
            try {
                const decoded = jwtDecode<{ exp: number }>(token);
                if (decoded.exp * 1000 > Date.now()) {
                    return true;
                }
            } catch (e) {
                return false;
            }
        }
        return false;
    }

    // When the application starts, if a token exists, try to decode it
    // This ensures user data is always fresh from the token if available
    if (accessToken.value) {
        decodeAndStoreUser(accessToken.value);
    }

    // Watch for changes in accessToken and re-decode user if it changes
    watch(accessToken, (newToken) => {
        if (newToken) {
            decodeAndStoreUser(newToken);
        } else {
            user.value = null; // Clear user if token is removed
            localStorage.removeItem('user');
        }
    }, { immediate: true }); // Run immediately on component mount

    // Listen for unauthorized events from the API client
    eventBus.on(EventType.Unauthorized, () => {
        console.log('Unauthorized event received. Logging out...');
        logout();
        eventBus.emit(EventType.ShowAlert, {
            type: 'error',
            title: '會話過期',
            message: '您的會話已過期，請重新登入。',
        });
    });

    return {
        accessToken,
        refreshToken,
        user,
        isAuthenticated,
        isAuthor,
        setTokens,
        setAccessToken,
        logout,
        checkAuth,
        updateUser,
    };
});