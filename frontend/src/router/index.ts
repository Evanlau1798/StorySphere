// src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../store/auth';

// 引入所有頁面組件
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import NovelDetailView from '@/views/NovelDetailView.vue';
import AuthorView from '@/views/AuthorView.vue';
import ProfileSettingsView from '@/views/ProfileSettingsView.vue';
import ReadingView from '@/views/ReadingView.vue';
import AuthorDashboardLayout from '@/views/author/AuthorDashboardLayout.vue';
import AuthorNovelList from '@/views/author/AuthorNovelList.vue';
import AuthorNovelEdit from '@/views/author/AuthorNovelEdit.vue';
import AuthorAnalytics from '@/views/author/AuthorAnalytics.vue';
import AuthorChapterEdit from '@/views/author/AuthorChapterEdit.vue';
import BookshelfView from '@/views/BookshelfView.vue'; // 引入書架頁面
import ExploreView from '@/views/ExploreView.vue'; // 新增探索頁面
import LeaderboardView from '@/views/LeaderboardView.vue'; // 新增排行榜頁面
import UpdatesView from '@/views/UpdatesView.vue'; // 新增最新更新頁面
import RecentViewedView from '@/views/RecentViewedView.vue'; // 新增最近瀏覽頁面

const routes: Array<RouteRecordRaw> = [
  { 
    path: '/', 
    name: 'Home', 
    component: HomeView 
  },
  { 
    path: '/explore', 
    name: 'Explore', 
    component: ExploreView 
  },
  { 
    path: '/leaderboard', 
    name: 'Leaderboard', 
    component: LeaderboardView 
  },
  {
    path: '/updates',
    name: 'Updates',
    component: UpdatesView
  },
  {
    path: '/recent',
    name: 'RecentViewed',
    component: RecentViewedView,
    meta: { requiresAuth: true } // 最近瀏覽需要登入才能查看
  },
  { 
    path: '/login', 
    name: 'Login', 
    component: LoginView 
  },
  { 
    path: '/register', 
    name: 'Register', 
    component: RegisterView 
  },
  { 
    path: '/novel/:id', 
    name: 'NovelDetail', 
    component: NovelDetailView, 
    props: true // 將路由參數 :id 作為 props 傳入組件
  },
  { 
    path: '/author/:id', 
    name: 'Author', 
    component: AuthorView, 
    props: true // 將路由參數 :id 作為 props 傳入組件
  },
  {
    path: '/read/:novelId/:chapterId',
    name: 'Reading',
    component: ReadingView,
    props: true
  },
  { 
    path: '/settings/profile', 
    name: 'ProfileSettings', 
    component: ProfileSettingsView,
    meta: { requiresAuth: true } // 標記此路由需要認證
  },
  {
    path: '/bookshelf',
    name: 'Bookshelf',
    component: BookshelfView,
    meta: { requiresAuth: true } // 書架需要登入才能查看
  },
  {
    path: '/dashboard',
    component: AuthorDashboardLayout,
    meta: { requiresAuth: true, requiresAuthor: true },
    children: [
      {
        path: '',
        name: 'AuthorDashboard',
        redirect: '/dashboard/novels'
      },
      {
        path: 'novels',
        name: 'AuthorNovelList',
        component: AuthorNovelList
      },
      {
        path: 'novels/new',
        name: 'AuthorNovelCreate',
        component: AuthorNovelEdit
      },
      {
        path: 'novels/:novelId/edit',
        name: 'AuthorNovelEdit',
        component: AuthorNovelEdit,
        props: true
      },
      {
        path: 'novels/:novelId/chapters/new',
        name: 'AuthorChapterCreate',
        component: AuthorChapterEdit,
        props: true
      },
      {
        path: 'novels/:novelId/chapters/:chapterId/edit',
        name: 'AuthorChapterEdit',
        component: AuthorChapterEdit,
        props: true
      },
      {
        path: 'analytics',
        name: 'AuthorAnalytics',
        component: AuthorAnalytics
      }
    ]
  }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(_to, _from, savedPosition) {
      if (savedPosition) {
        return savedPosition;
      } else {
        return { top: 0 };
      }
    },
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAuthor = to.matched.some(record => record.meta.requiresAuthor);

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (requiresAuthor && authStore.user?.role !== 'AUTHOR') {
    // 如果需要作者權限但使用者不是作者，可以導向到首頁或一個錯誤頁面
    next({ name: 'Home' }); 
  } else {
    next();
  }
});

export default router;