import apiClient from './client';
import type { User, UpdateProfileRequest, PaginatedResponse } from '../types';

export const usersApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    apiClient.get<PaginatedResponse<User>>('/users', { params }).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<User>(`/users/${id}`).then((r) => r.data),

  updateMe: (data: UpdateProfileRequest) =>
    apiClient.patch<User>('/users/me', data).then((r) => r.data),

  deactivate: (id: number) =>
    apiClient.patch<User>(`/users/${id}/deactivate`).then((r) => r.data),

  delete: (id: number) =>
    apiClient.delete(`/users/${id}`).then((r) => r.data),
};
