import apiClient from './client';
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectMember,
  PaginatedResponse,
} from '../types';

export const projectsApi = {
  list: (params?: { is_archived?: boolean; search?: string; limit?: number; offset?: number }) =>
    apiClient.get<PaginatedResponse<Project>>('/projects', { params }).then((r) => r.data),

  get: (id: number) =>
    apiClient.get<Project>(`/projects/${id}`).then((r) => r.data),

  create: (data: CreateProjectRequest) =>
    apiClient.post<Project>('/projects', data).then((r) => r.data),

  update: (id: number, data: UpdateProjectRequest) =>
    apiClient.patch<Project>(`/projects/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    apiClient.delete(`/projects/${id}`).then((r) => r.data),

  archive: (id: number) =>
    apiClient.patch<Project>(`/projects/${id}/archive`).then((r) => r.data),

  getMembers: (id: number) =>
    apiClient.get<PaginatedResponse<ProjectMember>>(`/projects/${id}/members`).then((r) => r.data),

  addMember: (projectId: number, userId: number) =>
    apiClient.post(`/projects/${projectId}/members`, { user_id: userId }).then((r) => r.data),

  removeMember: (projectId: number, userId: number) =>
    apiClient.delete(`/projects/${projectId}/members/${userId}`).then((r) => r.data),
};
