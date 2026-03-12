import apiClient from './client';
import type { Assignment, AssignUserRequest } from '../types';

export const assignmentsApi = {
  list: (projectId: number, taskId: number) =>
    apiClient
      .get<Assignment[]>(`/projects/${projectId}/tasks/${taskId}/assignments`)
      .then((r) => r.data),

  assign: (projectId: number, taskId: number, data: AssignUserRequest) =>
    apiClient
      .post<Assignment>(`/projects/${projectId}/tasks/${taskId}/assignments`, data)
      .then((r) => r.data),

  unassign: (projectId: number, taskId: number, userId: number) =>
    apiClient
      .delete(`/projects/${projectId}/tasks/${taskId}/assignments/${userId}`)
      .then((r) => r.data),
};
