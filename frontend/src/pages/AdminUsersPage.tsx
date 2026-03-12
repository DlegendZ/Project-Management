import { useEffect, useState, useCallback } from 'react';
import { Shield, UserX, Trash2, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { usersApi } from '../api/users';
import { useAuthStore } from '../store/authStore';
import { Navigate } from 'react-router-dom';
import { Spinner } from '../components/ui/Spinner';
import { Avatar } from '../components/ui/Avatar';
import { RoleBadge, Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { ConfirmModal } from '../components/ui/Modal';
import type { User } from '../types';
import { format, parseISO } from 'date-fns';
import toast from 'react-hot-toast';

const PAGE_SIZE = 20;

export function AdminUsersPage() {
  const { user: me } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');

  const [deactivateTarget, setDeactivateTarget] = useState<User | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  if (me?.role !== 'admin') return <Navigate to="/" replace />;

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await usersApi.list({ limit: PAGE_SIZE, offset: page * PAGE_SIZE });
      setUsers(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filtered = search
    ? users.filter(
        (u) =>
          u.username.toLowerCase().includes(search.toLowerCase()) ||
          u.email.toLowerCase().includes(search.toLowerCase())
      )
    : users;

  const handleDeactivate = async () => {
    if (!deactivateTarget) return;
    setActionLoading(true);
    try {
      await usersApi.deactivate(deactivateTarget.id);
      toast.success(`${deactivateTarget.username} deactivated`);
      setDeactivateTarget(null);
      fetchUsers();
    } catch {
      toast.error('Failed to deactivate user');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setActionLoading(true);
    try {
      await usersApi.delete(deleteTarget.id);
      toast.success(`${deleteTarget.username} deleted`);
      setDeleteTarget(null);
      fetchUsers();
    } catch {
      toast.error('Failed to delete user');
    } finally {
      setActionLoading(false);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="p-8 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 bg-indigo-900/50 border border-indigo-700/40 rounded-lg flex items-center justify-center">
          <Shield size={16} className="text-indigo-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">User Management</h1>
          <p className="text-slate-400 text-sm">{total} registered user{total !== 1 ? 's' : ''}</p>
        </div>
      </div>

      {/* Search */}
      <div className="mb-5 max-w-xs">
        <Input
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={<Search size={15} />}
        />
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-700/30">
                <th className="text-left px-4 py-3 text-slate-400 font-medium">User</th>
                <th className="text-left px-4 py-3 text-slate-400 font-medium">Role</th>
                <th className="text-left px-4 py-3 text-slate-400 font-medium">Status</th>
                <th className="text-left px-4 py-3 text-slate-400 font-medium">Joined</th>
                <th className="text-right px-4 py-3 text-slate-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr
                  key={u.id}
                  className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <Avatar name={u.username} size="sm" />
                      <div>
                        <p className="text-slate-200 font-medium">
                          {u.username}
                          {u.id === me?.id && (
                            <span className="ml-2 text-xs text-indigo-400">(you)</span>
                          )}
                        </p>
                        <p className="text-slate-500 text-xs">{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <RoleBadge role={u.role} />
                  </td>
                  <td className="px-4 py-3">
                    <Badge color={u.is_active ? 'green' : 'red'}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {format(parseISO(u.created_at), 'MMM d, yyyy')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      {u.id !== me?.id && u.is_active && (
                        <button
                          onClick={() => setDeactivateTarget(u)}
                          className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 px-2 py-1 rounded hover:bg-amber-900/20 transition-colors"
                          title="Deactivate"
                        >
                          <UserX size={13} /> Deactivate
                        </button>
                      )}
                      {u.id !== me?.id && (
                        <button
                          onClick={() => setDeleteTarget(u)}
                          className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 px-2 py-1 rounded hover:bg-red-900/20 transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={13} /> Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="text-center py-10 text-slate-500">No users found</div>
          )}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && !search && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-slate-500 text-sm">
            Page {page + 1} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-200 disabled:opacity-40"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-200 disabled:opacity-40"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Modals */}
      <ConfirmModal
        isOpen={!!deactivateTarget}
        onClose={() => setDeactivateTarget(null)}
        onConfirm={handleDeactivate}
        title="Deactivate User"
        message={`Deactivate "${deactivateTarget?.username}"? They won't be able to log in.`}
        confirmLabel="Deactivate"
        variant="danger"
        loading={actionLoading}
      />
      <ConfirmModal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete User"
        message={`Permanently delete "${deleteTarget?.username}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={actionLoading}
      />
    </div>
  );
}
