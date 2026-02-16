import axios, { AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://172.20.89.42:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          return api.request(error.config);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
}

export interface ContentItem {
  id: string;
  title: string;
  content: string;
  content_type: 'social' | 'video' | 'blog' | 'email';
  platforms: string[];
  created_at: string;
  match_score?: number;
  video_matches?: VideoMatch[];
}

export interface VideoMatch {
  id: string;
  title: string;
  match_score: number;
  reasoning: string;
  thumbnail_url?: string;
}

export interface VoiceProfile {
  id: string;
  name: string;
  style: 'professional' | 'casual' | 'educational';
  sample_content?: string;
}

// API Functions
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  
  register: (userData: {
    username: string;
    email: string;
    full_name: string;
    password: string;
    password_confirm: string;
  }) => api.post('/accounts/register/', userData),
  
  logout: () => api.post('/auth/logout/'),
  
  getProfile: () => api.get<User>('/accounts/profile/'),
};

export const contentAPI = {
  generate: (data: {
    topic: string;
    content_type: string;
    target_platforms: string[];
    voice_profile?: string;
    creativity_level: number;
    include_hashtags: boolean;
    include_emojis: boolean;
    find_videos: boolean;
  }) => api.post('/content/generate/', data),
  
  list: (params?: {
    content_type?: string;
    limit?: number;
    offset?: number;
  }) => api.get<{ results: ContentItem[] }>('/content/', { params }),
  
  get: (id: string) => api.get<ContentItem>(`/content/${id}/`),
  
  delete: (id: string) => api.delete(`/content/${id}/`),
};

export const videoAPI = {
  upload: (file: File, title: string, description?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) formData.append('description', description);
    
    return api.post('/video/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  list: () => api.get('/video/'),
  
  getMatches: (contentId: string) =>
    api.get<{ matches: VideoMatch[] }>(`/video/matches/${contentId}/`),
};

export const voiceProfileAPI = {
  list: () => api.get<VoiceProfile[]>('/accounts/voice-profiles/'),
  
  create: (data: {
    name: string;
    style: string;
    sample_posts: string[];
    platforms: string[];
    niche?: string;
  }) => api.post('/accounts/voice-profiles/', data),
  
  delete: (id: string) => api.delete(`/accounts/voice-profiles/${id}/`),
};

export default api;