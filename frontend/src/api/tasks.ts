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

  mine: (params?: Pick<TaskFilters, 'status' | 'priority' | 'sort_by' | 'sort_dir' | 'limit' | 'offset'>) =>
    apiClient.get<PaginatedResponse<Task>>('/tasks/mine', { params }).then((r) => r.data),

  assign: (projectId: number, taskId: number, userId: number) =>
    apiClient
      .post(`/projects/${projectId}/tasks/${taskId}/assignments`, { user_id: userId })
      .then((r) => r.data),

  unassign: (projectId: number, taskId: number, userId: number) =>
    apiClient
      .delete(`/projects/${projectId}/tasks/${taskId}/assignments/${userId}`)
      .then((r) => r.data),
};
