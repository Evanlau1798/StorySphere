// src/types.ts

export interface Author {
  username: string;
}

// 新增 Chapter 介面
export interface Chapter {
  id: number;
  title: string;
  order: number;
  published_at: string;
  updated_at: string; // 新增：最後更新時間
  volume?: number | null; // 新增：章節所屬的卷 ID (可選，因為章節可能不屬於任何卷)
  status?: 'DRAFT' | 'PUBLISHED';
  content?: string;
}

// 新增 Volume 介面
export interface Volume {
  id: number;
  title: string;
  order: number;
  chapters: Chapter[];
  description: string;
  cover_image: string | null;
}

export interface Novel {
  id: number;
  title: string;
  description: string;
  cover_image: string | null;
  status: 'ONGOING' | 'COMPLETED' | 'HIATUS';
  updated_at: string;
  created_at: string;
  // 將 author 的類型改為 AuthorSummary
  author: AuthorSummary;
  volumes: Volume[]; // 將 chapters 替換為 volumes
  chapters_without_volume?: Chapter[];
  views: number; // Changed from total_views to match backend default view field or annotated one
  author_name?: string;
  category: string;
  latest_chapter?: string;
  latest_chapter_updated_at?: string;
}

// API 回應的分頁格式
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 用於小說列表頁和詳情頁中顯示的作者摘要資訊
export interface AuthorSummary {
  user_id: number;
  pen_name: string;
  username: string;
}

// 用於作者頁面中顯示的、簡化版的小說資訊
export interface SimpleNovel {
  id: number;
  title: string;
  cover_image: string | null;
  status: 'ONGOING' | 'COMPLETED' | 'HIATUS';
  updated_at: string;
  description: string;
  category: string;
}

// 作者公開頁面的完整資料
export interface AuthorProfile {
  user_id: number;
  username: string;
  pen_name: string;
  bio: string;
  avatar: string | null;
  role: 'READER' | 'AUTHOR' | 'ADMIN'; // 新增 role 屬性
  // 新增：小說列表
  novels: SimpleNovel[];
}

// 用於表示當前登入使用者的完整個人資料
export interface UserProfile {
  user_id?: number;
  username?: string;
  pen_name?: string;
  bio?: string;
  avatar: string | null;
  role?: 'READER' | 'AUTHOR' | 'ADMIN';
}

// 新增 ReadingProgress 介面
export interface ReadingProgress {
  user_id: number;
  novel_id: number;
  last_read_chapter_id: number;
  novel_detail: Novel; // 新增 novel_detail 屬性
}