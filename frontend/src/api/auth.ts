import apiClient from './client';
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types';

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>('/auth/login', data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<User>('/auth/register', data).then((r) => r.data),

  me: () =>
    apiClient.get<User>('/auth/me').then((r) => r.data),

  logout: (refresh_token: string) =>
    apiClient.post('/auth/logout', { refresh_token }).then((r) => r.data),

  refresh: (refresh_token: string) =>
    apiClient.post<TokenResponse>('/auth/refresh', { refresh_token }).then((r) => r.data),
};
