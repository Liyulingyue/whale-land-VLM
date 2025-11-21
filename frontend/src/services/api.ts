import axios from 'axios';
import type { SessionInfo, ChatResponse, ImageUploadResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const gameService = {
  // 创建会话
  createSession: async (sessionId: string, configPath?: string): Promise<SessionInfo> => {
    const response = await api.post('/session/create', {
      session_id: sessionId,
      config_path: configPath || 'config/police.yaml',
    });
    return response.data;
  },

  // 获取会话状态
  getSessionStatus: async (sessionId: string): Promise<SessionInfo> => {
    const response = await api.get(`/session/${sessionId}/status`);
    return response.data;
  },

  // 重置会话
  resetSession: async (sessionId: string): Promise<SessionInfo> => {
    const response = await api.post(`/session/${sessionId}/reset`);
    return response.data;
  },

  // 发送聊天消息
  sendMessage: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },

  // 上传图片
  uploadImage: async (sessionId: string, file: File): Promise<ImageUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/image/upload?session_id=${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 提交物品
  submitItem: async (sessionId: string, itemName: string) => {
    const response = await api.post('/item/submit', {
      session_id: sessionId,
      item_name: itemName,
    });
    return response.data;
  },

  // 获取可用物品
  getItems: async (sessionId: string): Promise<{ items: string[] }> => {
    const response = await api.get(`/items/${sessionId}`);
    return response.data;
  },
};

export default api;
