import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Settings,
  Users,
  Search,
  Filter,
  Plus,
  UserPlus,
  UserMinus,
  Pencil,
  X,
} from 'lucide-react';
import { projectsApi } from '../api/projects';
import { tasksApi } from '../api/tasks';
import { usersApi } from '../api/users';
import { useAuthStore } from '../store/authStore';
import { KanbanBoard } from '../components/kanban/KanbanBoard';
import { TaskModal } from '../components/tasks/TaskModal';
import { ConfirmModal, Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Input, Select } from '../components/ui/Input';
import { Spinner } from '../components/ui/Spinner';
import { Avatar } from '../components/ui/Avatar';
import { Badge } from '../components/ui/Badge';
import type { Project, Task, TaskStatus, ProjectMember, User, TaskFilters } from '../types';
import toast from 'react-hot-toast';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const projectId = Number(id);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [loading, setLoading] = useState(true);

  // UI state
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [defaultStatus, setDefaultStatus] = useState<TaskStatus>('todo');
  const [deleteTarget, setDeleteTarget] = useState<Task | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [membersOpen, setMembersOpen] = useState(false);

  // Filters
  const [filters, setFilters] = useState<TaskFilters>({ limit: 200 });
  const [searchText, setSearchText] = useState('');

  const isOwner = project?.owner_id === user?.id || user?.role === 'admin';

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [proj, taskData, memberData] = await Promise.all([
        projectsApi.get(projectId),
        tasksApi.list(projectId, { ...filters, q: searchText || undefined }),
        projectsApi.getMembers(projectId),
      ]);
      setProject(proj);
      setTasks(taskData.items);
      setMembers(memberData.items);
    } catch {
      toast.error('Failed to load project');
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  }, [projectId, filters, searchText, navigate]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleStatusChange = async (taskId: number, newStatus: TaskStatus) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );
    try {
      await tasksApi.update(projectId, taskId, { status: newStatus });
      toast.success('Status updated');
    } catch {
      fetchAll();
      toast.error('Failed to update status');
    }
  };

  const handleCreateTask = async (data: import('../types').CreateTaskRequest) => {
    const created = await tasksApi.create(projectId, data);
    toast.success('Task created');
    setTasks((prev) => [...prev, created]);
  };

  const handleEditTask = async (data: import('../types').UpdateTaskRequest) => {
    if (!editingTask) return;
    const updated = await tasksApi.update(projectId, editingTask.id, data);
    toast.success('Task updated');
    setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
  };

  const handleTaskSubmit = async (data: import('../types').CreateTaskRequest | import('../types').UpdateTaskRequest) => {
    if (editingTask) {
      await handleEditTask(data);
    } else {
      await handleCreateTask(data as import('../types').CreateTaskRequest);
    }
  };

  const handleDeleteTask = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await tasksApi.delete(projectId, deleteTarget.id);
      toast.success('Task deleted');
      setTasks((prev) => prev.filter((t) => t.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch {
      toast.error('Failed to delete task');
    } finally {
      setDeleteLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!project) return null;

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Top bar */}
      <header className="flex-shrink-0 flex items-center gap-4 px-6 py-4 border-b border-slate-700 bg-slate-900">
        <Link to="/projects" className="text-slate-400 hover:text-slate-200 transition-colors">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="text-slate-100 font-semibold text-lg truncate">{project.name}</h1>
            {project.is_archived && <Badge color="amber">Archived</Badge>}
          </div>
          {project.description && (
            <p className="text-slate-500 text-xs truncate">{project.description}</p>
          )}
        </div>

        {/* Members avatars */}
        <button
          onClick={() => setMembersOpen(true)}
          className="flex items-center -space-x-2 hover:space-x-0.5 transition-all"
        >
          {members.slice(0, 4).map((m) => (
            <Avatar key={m.id} name={m.username} size="sm" className="border-2 border-slate-900" />
          ))}
          {members.length > 4 && (
            <span className="text-xs text-slate-400 pl-3">+{members.length - 4}</span>
          )}
          <span className="text-slate-400 text-xs pl-2 flex items-center gap-1">
            <Users size={13} /> {members.length}
          </span>
        </button>

        {isOwner && (
          <Button
            variant="ghost"
            size="sm"
            icon={<Settings size={15} />}
            onClick={() => setSettingsOpen(true)}
          >
            Settings
          </Button>
        )}
        <Button
          size="sm"
          icon={<Plus size={15} />}
          onClick={() => {
            setEditingTask(null);
            setDefaultStatus('todo');
            setTaskModalOpen(true);
          }}
        >
          Add Task
        </Button>
      </header>

      {/* Filter bar */}
      <div className="flex-shrink-0 flex items-center gap-3 px-6 py-3 border-b border-slate-700/50 bg-slate-900/50">
        <div className="w-56">
          <Input
            placeholder="Search tasks..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            icon={<Search size={14} />}
          />
        </div>
        <Select
          options={[
            { value: '', label: 'All Priorities' },
            { value: 'high', label: 'High' },
            { value: 'medium', label: 'Medium' },
            { value: 'low', label: 'Low' },
          ]}
          value={filters.priority ?? ''}
          onChange={(e) =>
            setFilters((f) => ({ ...f, priority: (e.target.value as TaskFilters['priority']) || undefined }))
          }
        />
        <Select
          options={[
            { value: '', label: 'All Members' },
            ...members.map((m) => ({ value: String(m.id), label: m.username })),
          ]}
          value={filters.assignee_id ? String(filters.assignee_id) : ''}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              assignee_id: e.target.value ? Number(e.target.value) : undefined,
            }))
          }
        />
        {(filters.priority || filters.assignee_id || searchText) && (
          <button
            onClick={() => { setFilters({ limit: 200 }); setSearchText(''); }}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-700"
          >
            <X size={12} /> Clear
          </button>
        )}
        <div className="flex items-center gap-1 text-xs text-slate-500 ml-auto">
          <Filter size={12} />
          {tasks.length} task{tasks.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Kanban board */}
      <div className="flex-1 overflow-auto p-6">
        <KanbanBoard
          tasks={tasks}
          onStatusChange={handleStatusChange}
          onAddTask={(status) => {
            setEditingTask(null);
            setDefaultStatus(status);
            setTaskModalOpen(true);
          }}
          onEditTask={(task) => {
            setEditingTask(task);
            setTaskModalOpen(true);
          }}
          onDeleteTask={setDeleteTarget}
          isOwner={isOwner}
        />
      </div>

      {/* Task modal */}
      <TaskModal
        isOpen={taskModalOpen}
        onClose={() => { setTaskModalOpen(false); setEditingTask(null); }}
        onSubmit={handleTaskSubmit}
        task={editingTask}
        defaultStatus={defaultStatus}
      />

      {/* Delete task confirm */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteTask}
        title="Delete Task"
        message={`Delete "${deleteTarget?.title}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={deleteLoading}
      />

      {/* Project settings modal */}
      {isOwner && (
        <ProjectSettingsModal
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          project={project}
          onUpdated={(p) => setProject(p)}
        />
      )}

      {/* Members modal */}
      <MembersModal
        isOpen={membersOpen}
        onClose={() => setMembersOpen(false)}
        projectId={projectId}
        members={members}
        isOwner={isOwner}
        onChanged={fetchAll}
      />
    </div>
  );
}

// ─── Project Settings Modal ───────────────────────────────────────────────────

function ProjectSettingsModal({
  isOpen,
  onClose,
  project,
  onUpdated,
}: {
  isOpen: boolean;
  onClose: () => void;
  project: Project;
  onUpdated: (p: Project) => void;
}) {
  const [form, setForm] = useState({ name: project.name, description: project.description ?? '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) setForm({ name: project.name, description: project.description ?? '' });
  }, [isOpen, project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updated = await projectsApi.update(project.id, {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
      });
      toast.success('Project updated');
      onUpdated(updated);
      onClose();
    } catch {
      toast.error('Failed to update project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Project Settings">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Name"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
        />
        <div className="flex flex-col gap-1">
          <label className="text-sm text-slate-300 font-medium">Description</label>
          <textarea
            className="w-full rounded-lg bg-slate-700 border border-slate-600 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 px-3 py-2 resize-none text-sm"
            rows={3}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </div>
        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading} icon={<Pencil size={14} />}>Save</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Members Modal ────────────────────────────────────────────────────────────

function MembersModal({
  isOpen,
  onClose,
  projectId,
  members,
  isOwner,
  onChanged,
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  members: ProjectMember[];
  isOwner: boolean;
  onChanged: () => void;
}) {
  const { user } = useAuthStore();
  const [addEmail, setAddEmail] = useState('');
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [addLoading, setAddLoading] = useState(false);
  const [removeLoading, setRemoveLoading] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen && isOwner) {
      usersApi.list({ limit: 100 }).then((d) => setAllUsers(d.items)).catch(() => {});
    }
  }, [isOpen, isOwner]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const found = allUsers.find(
      (u) => u.email.toLowerCase() === addEmail.toLowerCase() ||
             u.username.toLowerCase() === addEmail.toLowerCase()
    );
    if (!found) { toast.error('User not found'); return; }
    if (members.find((m) => m.id === found.id)) { toast.error('Already a member'); return; }
    setAddLoading(true);
    try {
      await projectsApi.addMember(projectId, found.id);
      toast.success(`${found.username} added`);
      setAddEmail('');
      onChanged();
    } catch (err) {
      const axiosErr = err as AxiosError<ApiError>;
      toast.error(axiosErr.response?.data?.error?.message ?? 'Failed to add member');
    } finally {
      setAddLoading(false);
    }
  };

  const handleRemove = async (memberId: number) => {
    setRemoveLoading(memberId);
    try {
      await projectsApi.removeMember(projectId, memberId);
      toast.success('Member removed');
      onChanged();
    } catch {
      toast.error('Failed to remove member');
    } finally {
      setRemoveLoading(null);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Project Members" size="md">
      <div className="flex flex-col gap-4">
        {isOwner && (
          <form onSubmit={handleAdd} className="flex gap-2">
            <Input
              placeholder="Username or email"
              value={addEmail}
              onChange={(e) => setAddEmail(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" loading={addLoading} icon={<UserPlus size={14} />}>
              Add
            </Button>
          </form>
        )}

        <div className="flex flex-col gap-2 max-h-72 overflow-y-auto">
          {members.map((m) => (
            <div
              key={m.id}
              className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <Avatar name={m.username} size="sm" />
                <div>
                  <p className="text-slate-200 text-sm font-medium">{m.username}</p>
                  <p className="text-slate-500 text-xs">{m.email}</p>
                </div>
              </div>
              {isOwner && m.id !== user?.id && (
                <button
                  onClick={() => handleRemove(m.id)}
                  disabled={removeLoading === m.id}
                  className="text-slate-500 hover:text-red-400 transition-colors disabled:opacity-50"
                >
                  {removeLoading === m.id ? <Spinner size="sm" /> : <UserMinus size={15} />}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
}
