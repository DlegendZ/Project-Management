import apiClient from './client';
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskFilters, PaginatedResponse } from '../types';

export const tasksApi = {
  list: (projectId: number, params?: TaskFilters) =>
    apiClient
      .get<PaginatedResponse<Task>>(`/projects/${projectId}/tasks`, { params })
      .then((r) => r.data),

  get: (projectId: number, taskId: number) =>
    apiClient.get<Task>(`/projects/${projectId}/tasks/${taskId}`).then((r) => r.data),

  create: (projectId: number, data: CreateTaskRequest) =>
    apiClient.post<Task>(`/projects/${projectId}/tasks`, data).then((r) => r.data),

  update: (projectId: number, taskId: number, data: UpdateTaskRequest) =>
    apiClient.patch<Task>(`/projects/${projectId}/tasks/${taskId}`, data).then((r) => r.data),

  delete: (projectId: number, taskId: number) =>
    apiClient.delete(`/projects/${projectId}/tasks/${taskId}`).then((r) => r.data),

  mine: (params?: { limit?: number; offset?: number }) =>
    apiClient.get<PaginatedResponse<Task>>('/tasks/mine', { params }).then((r) => r.data),
};
