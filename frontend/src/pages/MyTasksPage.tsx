import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { CheckSquare, Calendar, FolderKanban, ChevronLeft, ChevronRight } from 'lucide-react';
import { tasksApi } from '../api/tasks';
import { Spinner } from '../components/ui/Spinner';
import { StatusBadge, PriorityBadge } from '../components/ui/Badge';
import { Select } from '../components/ui/Input';
import type { Task, TaskFilters } from '../types';
import { format, parseISO, isPast } from 'date-fns';

const PAGE_SIZE = 20;

export function MyTasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<TaskFilters>({
    sort_by: 'due_date',
    sort_dir: 'asc',
  });

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const data = await tasksApi.mine({
        ...filters,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      });
      setTasks(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">My Tasks</h1>
        <p className="text-slate-400 text-sm mt-1">
          {total} task{total !== 1 ? 's' : ''} assigned to you
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <Select
          options={[
            { value: '', label: 'All Statuses' },
            { value: 'todo', label: 'To Do' },
            { value: 'in_progress', label: 'In Progress' },
            { value: 'done', label: 'Done' },
          ]}
          value={filters.status ?? ''}
          onChange={(e) =>
            setFilters((f) => ({ ...f, status: (e.target.value as TaskFilters['status']) || undefined }))
          }
        />
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
            { value: 'due_date', label: 'Sort: Due Date' },
            { value: 'priority', label: 'Sort: Priority' },
            { value: 'created_at', label: 'Sort: Created' },
          ]}
          value={filters.sort_by ?? 'due_date'}
          onChange={(e) =>
            setFilters((f) => ({ ...f, sort_by: e.target.value as TaskFilters['sort_by'] }))
          }
        />
      </div>

      {/* Task list */}
      {loading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-20 bg-slate-800 border border-slate-700 rounded-xl">
          <CheckSquare size={48} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No tasks assigned to you</p>
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-2">
            {tasks.map((task) => (
              <TaskRow key={task.id} task={task} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
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
        </>
      )}
    </div>
  );
}

function TaskRow({ task }: { task: Task }) {
  const isOverdue = task.due_date && task.status !== 'done' && isPast(parseISO(task.due_date));

  return (
    <div className="flex items-center gap-4 p-4 bg-slate-800 border border-slate-700 rounded-xl hover:border-slate-500 transition-colors">
      {/* Status indicator */}
      <div
        className={`w-2 h-2 rounded-full flex-shrink-0 ${
          task.status === 'done'
            ? 'bg-green-400'
            : task.status === 'in_progress'
            ? 'bg-blue-400'
            : 'bg-slate-500'
        }`}
      />

      {/* Title */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${task.status === 'done' ? 'text-slate-500 line-through' : 'text-slate-200'}`}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-slate-500 truncate mt-0.5">{task.description}</p>
        )}
      </div>

      {/* Project link */}
      <Link
        to={`/projects/${task.project_id}`}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-400 transition-colors flex-shrink-0"
      >
        <FolderKanban size={12} />
        Project #{task.project_id}
      </Link>

      {/* Due date */}
      {task.due_date && (
        <span
          className={`flex items-center gap-1 text-xs flex-shrink-0 ${
            isOverdue ? 'text-red-400' : 'text-slate-500'
          }`}
        >
          <Calendar size={12} />
          {format(parseISO(task.due_date), 'MMM d')}
        </span>
      )}

      {/* Badges */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <PriorityBadge priority={task.priority} />
        <StatusBadge status={task.status} />
      </div>
    </div>
  );
}
