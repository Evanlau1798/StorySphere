<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">使用者管理</h1>

    <div class="mb-4">
        <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="搜尋使用者名稱或 Email..." 
            class="w-full md:w-1/3 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white"
        >
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
        <thead class="bg-gray-100 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">使用者名稱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Email</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">角色</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">加入時間</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">#{{ user.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{{ user.username }}</span>
                </div>
            </td>
             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ user.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="{
                        'bg-green-100 text-green-800': user.role === 'READER',
                        'bg-blue-100 text-blue-800': user.role === 'AUTHOR',
                        'bg-red-100 text-red-800': user.role === 'ADMIN'
                    }"
                >
                    {{ getRoleName(user.role) }}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(user.date_joined) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <select 
                    v-if="user.id !== 1"
                    :value="user.role" 
                    @change="(e) => changeRole(user, (e.target as HTMLSelectElement).value)"
                    class="ml-2 text-sm border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 dark:bg-gray-700 dark:text-white"
                >
                    <option value="READER">讀者</option>
                    <option value="AUTHOR">作者</option>
                    <option value="ADMIN">管理員</option>
                </select>
                <span v-else class="text-gray-400 italic text-xs">超級管理員 (鎖定)</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import { eventBus, EventType } from '../../composables/useEventBus';

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    date_joined: string;
}

const users = ref<User[]>([]);
const searchQuery = ref('');
let searchTimeout: any = null;

const fetchUsers = async () => {
    try {
        const response = await api.get('admin/users/', {
            params: { q: searchQuery.value }
        });
        users.value = response.data;
    } catch (error) {
        console.error('Failed to fetch users', error);
    }
};

const handleSearch = () => {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetchUsers();
    }, 300);
};

const changeRole = async (user: User, newRole: string) => {
    if (!confirm(`確定要將 ${user.username} 的角色更改為 ${newRole} 嗎？`)) {
        // Reset select if cancelled (trickier with v-model, but rerendering list helps)
        // simpler way: manually force update or re-fetch
        fetchUsers(); 
        return;
    }

    try {
        await api.patch(`admin/${user.id}/update_role/`, { role: newRole });
         eventBus.emit(EventType.ShowAlert, {
            type: 'success',
            title: '更新成功',
            message: `已將 ${user.username} 更新為 ${newRole}`,
        });
        user.role = newRole; // Optimistic update
    } catch (error) {
        console.error('Failed to update role', error);
        eventBus.emit(EventType.ShowAlert, {
            type: 'error',
            title: '更新失敗',
            message: '無法更新角色，請稍後再試。',
        });
        fetchUsers(); // Revert on failure
    }
};

const getRoleName = (role: string) => {
    const map: Record<string, string> = {
        'READER': '讀者',
        'AUTHOR': '作者',
        'ADMIN': '管理員'
    };
    return map[role] || role;
};

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW');
};

onMounted(() => {
    fetchUsers();
});
</script>
