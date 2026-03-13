// ─── Auth ────────────────────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ─── User ─────────────────────────────────────────────────────────────────────

export type UserRole = 'admin' | 'user';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  username?: string;
  email?: string;
  new_password?: string;
  current_password?: string;
}

// ─── Project ──────────────────────────────────────────────────────────────────

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  owner?: User;
  member_count?: number;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
}

export interface ProjectMember {
  id: number;
  username: string;
  email: string;
  role: UserRole;
}

// ─── Task ─────────────────────────────────────────────────────────────────────

export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface AssigneeInfo {
  id: number;
  username: string;
  email: string;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  project_id: number;
  created_by: number;
  created_at: string;
  updated_at: string;
  assignees?: AssigneeInfo[];
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  assignee_ids?: number[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string | null;
  assignee_ids?: number[];
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number;
  due_date_from?: string;
  due_date_to?: string;
  is_overdue?: boolean;
  created_by?: number;
  q?: string;
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'updated_at';
  sort_dir?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

// ─── Assignment ───────────────────────────────────────────────────────────────

export interface Assignment {
  id: number;
  task_id: number;
  user_id: number;
  assigned_by: number;
  assigned_at: string;
  user?: User;
}

export interface AssignUserRequest {
  user_id: number;
}

// ─── Pagination ───────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  total: number;
  limit: number;
  offset: number;
  items: T[];
}

// ─── Error ────────────────────────────────────────────────────────────────────

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown> | null;
  };
}
