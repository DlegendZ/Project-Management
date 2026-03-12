import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FolderKanban, CheckSquare, Clock, AlertTriangle, ArrowRight } from 'lucide-react';
import { projectsApi } from '../api/projects';
import { tasksApi } from '../api/tasks';
import { useAuthStore } from '../store/authStore';
import { Spinner } from '../components/ui/Spinner';
import { StatusBadge, PriorityBadge } from '../components/ui/Badge';
import { format, parseISO } from 'date-fns';
import type { Project, Task } from '../types';

interface Stats {
  totalProjects: number;
  totalTasks: number;
  inProgressTasks: number;
  overdueTasks: number;
}

export function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [myTasks, setMyTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [projectsData, myTasksData, overdueData] = await Promise.all([
          projectsApi.list({ limit: 100 }),
          tasksApi.mine({ limit: 5 }),
          tasksApi.mine({ limit: 100 }),
        ]);

        const inProgress = overdueData.items.filter((t) => t.status === 'in_progress').length;
        const overdue = overdueData.items.filter((t) => {
          if (!t.due_date || t.status === 'done') return false;
          return new Date(t.due_date) < new Date();
        }).length;

        setStats({
          totalProjects: projectsData.total,
          totalTasks: overdueData.total,
          inProgressTasks: inProgress,
          overdueTasks: overdue,
        });
        setRecentProjects(projectsData.items.slice(0, 4));
        setMyTasks(myTasksData.items);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  const statCards = [
    { label: 'Total Projects', value: stats?.totalProjects ?? 0, icon: FolderKanban, color: 'text-indigo-400', bg: 'bg-indigo-900/30 border-indigo-700/40' },
    { label: 'My Tasks', value: stats?.totalTasks ?? 0, icon: CheckSquare, color: 'text-blue-400', bg: 'bg-blue-900/30 border-blue-700/40' },
    { label: 'In Progress', value: stats?.inProgressTasks ?? 0, icon: Clock, color: 'text-amber-400', bg: 'bg-amber-900/30 border-amber-700/40' },
    { label: 'Overdue', value: stats?.overdueTasks ?? 0, icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-900/30 border-red-700/40' },
  ];

  return (
    <div className="p-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-100">
          Good {getTimeOfDay()},{' '}
          <span className="text-indigo-400">{user?.username}</span> 👋
        </h1>
        <p className="text-slate-400 mt-1 text-sm">Here's what's happening with your projects today.</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className={`rounded-xl border p-5 ${bg}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-sm">{label}</span>
              <Icon size={18} className={color} />
            </div>
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-slate-100 font-semibold">Recent Projects</h2>
            <Link
              to="/projects"
              className="text-indigo-400 hover:text-indigo-300 text-sm flex items-center gap-1"
            >
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {recentProjects.length === 0 ? (
            <div className="text-center py-8">
              <FolderKanban size={32} className="text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500 text-sm">No projects yet</p>
              <Link to="/projects" className="text-indigo-400 text-sm hover:text-indigo-300">
                Create one →
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {recentProjects.map((p) => (
                <Link
                  key={p.id}
                  to={`/projects/${p.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-700 transition-colors group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-indigo-900/50 border border-indigo-700/40 flex items-center justify-center flex-shrink-0">
                      <FolderKanban size={14} className="text-indigo-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-slate-200 text-sm font-medium truncate">{p.name}</p>
                      {p.description && (
                        <p className="text-slate-500 text-xs truncate">{p.description}</p>
                      )}
                    </div>
                  </div>
                  <ArrowRight size={14} className="text-slate-600 group-hover:text-slate-400 flex-shrink-0" />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* My Tasks */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-slate-100 font-semibold">My Assigned Tasks</h2>
            <Link
              to="/tasks/mine"
              className="text-indigo-400 hover:text-indigo-300 text-sm flex items-center gap-1"
            >
              View all <ArrowRight size={14} />
            </Link>
          </div>
          {myTasks.length === 0 ? (
            <div className="text-center py-8">
              <CheckSquare size={32} className="text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500 text-sm">No tasks assigned to you</p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {myTasks.map((t) => (
                <div
                  key={t.id}
                  className="flex items-start justify-between p-3 rounded-lg bg-slate-700/50 border border-slate-700"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-200 text-sm font-medium truncate">{t.title}</p>
                    {t.due_date && (
                      <p className="text-slate-500 text-xs mt-0.5">
                        Due {format(parseISO(t.due_date), 'MMM d, yyyy')}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                    <PriorityBadge priority={t.priority} />
                    <StatusBadge status={t.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getTimeOfDay() {
  const h = new Date().getHours();
  if (h < 12) return 'morning';
  if (h < 17) return 'afternoon';
  return 'evening';
}
