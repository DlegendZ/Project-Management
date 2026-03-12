import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, FolderKanban, Archive, MoreVertical, Trash2 } from 'lucide-react';
import { projectsApi } from '../api/projects';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { ConfirmModal } from '../components/ui/Modal';
import { Spinner } from '../components/ui/Spinner';
import { Badge } from '../components/ui/Badge';
import type { Project, CreateProjectRequest } from '../types';
import toast from 'react-hot-toast';
import { format, parseISO } from 'date-fns';

export function ProjectsPage() {
  const { user } = useAuthStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [openMenu, setOpenMenu] = useState<number | null>(null);

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const data = await projectsApi.list({
        is_archived: showArchived ? undefined : false,
        search: search || undefined,
      });
      setProjects(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [search, showArchived]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const handleArchive = async (p: Project) => {
    await projectsApi.archive(p.id);
    toast.success(p.is_archived ? 'Project unarchived' : 'Project archived');
    fetchProjects();
    setOpenMenu(null);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await projectsApi.delete(deleteTarget.id);
      toast.success('Project deleted');
      setDeleteTarget(null);
      fetchProjects();
    } catch {
      toast.error('Failed to delete project');
    } finally {
      setDeleteLoading(false);
    }
  };

  const isOwnerOrAdmin = (p: Project) =>
    user?.role === 'admin' || p.owner_id === user?.id;

  return (
    <div className="p-8 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Projects</h1>
          <p className="text-slate-400 text-sm mt-1">{total} project{total !== 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => setCreateOpen(true)} icon={<Plus size={16} />}>
          New Project
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex-1 max-w-xs">
          <Input
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search size={16} />}
          />
        </div>
        <button
          onClick={() => setShowArchived((v) => !v)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm border transition-colors ${
            showArchived
              ? 'border-indigo-500 bg-indigo-900/30 text-indigo-300'
              : 'border-slate-600 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Archive size={15} />
          {showArchived ? 'Hide Archived' : 'Show Archived'}
        </button>
      </div>

      {/* Project grid */}
      {loading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : projects.length === 0 ? (
        <div className="text-center py-20 bg-slate-800 border border-slate-700 rounded-xl">
          <FolderKanban size={48} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No projects found</p>
          <Button className="mt-4" onClick={() => setCreateOpen(true)} icon={<Plus size={16} />}>
            Create Project
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              className="relative bg-slate-800 border border-slate-700 rounded-xl p-5 hover:border-slate-500 transition-colors group"
            >
              {/* Menu button */}
              {isOwnerOrAdmin(p) && (
                <div className="absolute top-3 right-3">
                  <button
                    onClick={(e) => { e.preventDefault(); setOpenMenu(openMenu === p.id ? null : p.id); }}
                    className="text-slate-500 hover:text-slate-300 p-1 rounded"
                  >
                    <MoreVertical size={15} />
                  </button>
                  {openMenu === p.id && (
                    <div
                      className="absolute right-0 top-7 z-20 w-40 bg-slate-700 border border-slate-600 rounded-lg shadow-xl overflow-hidden"
                      onMouseLeave={() => setOpenMenu(null)}
                    >
                      <button
                        onClick={() => handleArchive(p)}
                        className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-slate-300 hover:bg-slate-600 transition-colors"
                      >
                        <Archive size={14} />
                        {p.is_archived ? 'Unarchive' : 'Archive'}
                      </button>
                      <button
                        onClick={() => { setDeleteTarget(p); setOpenMenu(null); }}
                        className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-red-400 hover:bg-red-900/30 transition-colors"
                      >
                        <Trash2 size={14} />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              )}

              <Link to={`/projects/${p.id}`} className="block">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-indigo-900/50 border border-indigo-700/40 flex items-center justify-center flex-shrink-0">
                    <FolderKanban size={16} className="text-indigo-400" />
                  </div>
                  <div className="min-w-0 flex-1 pr-6">
                    <h3 className="text-slate-200 font-semibold text-sm truncate">{p.name}</h3>
                    {p.description && (
                      <p className="text-slate-500 text-xs mt-0.5 line-clamp-2">{p.description}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  {p.is_archived && <Badge color="amber">Archived</Badge>}
                  <span className="text-slate-600 text-xs ml-auto">
                    {format(parseISO(p.created_at), 'MMM d, yyyy')}
                  </span>
                </div>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      <CreateProjectModal
        isOpen={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={fetchProjects}
      />

      {/* Delete confirm */}
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Project"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? All tasks will be permanently deleted.`}
        confirmLabel="Delete"
        loading={deleteLoading}
      />
    </div>
  );
}

// ─── Create Project Modal ─────────────────────────────────────────────────────

function CreateProjectModal({
  isOpen,
  onClose,
  onCreated,
}: {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<CreateProjectRequest>({ name: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) { setForm({ name: '', description: '' }); setError(''); }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) { setError('Name is required'); return; }
    setLoading(true);
    try {
      await projectsApi.create({ name: form.name.trim(), description: form.description || undefined });
      toast.success('Project created!');
      onCreated();
      onClose();
    } catch {
      toast.error('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Project">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Project Name"
          placeholder="My awesome project"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          error={error}
          autoFocus
        />
        <div className="flex flex-col gap-1">
          <label className="text-sm text-slate-300 font-medium">Description (optional)</label>
          <textarea
            className="w-full rounded-lg bg-slate-700 border border-slate-600 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 px-3 py-2 resize-none text-sm"
            rows={3}
            placeholder="What's this project about?"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </div>
        <div className="flex justify-end gap-3 pt-1">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading}>Create Project</Button>
        </div>
      </form>
    </Modal>
  );
}
