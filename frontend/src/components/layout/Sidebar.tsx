import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Users,
  LogOut,
  User,
  Trello,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { Avatar } from '../ui/Avatar';
import toast from 'react-hot-toast';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/projects', label: 'Projects', icon: FolderKanban },
  { to: '/tasks/mine', label: 'My Tasks', icon: CheckSquare },
];

export function Sidebar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Logged out');
    navigate('/login');
  };

  return (
    <aside className="w-64 flex-shrink-0 bg-slate-800 border-r border-slate-700 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-700">
        <div className="w-8 h-8 bg-indigo-600 rounded-xl flex items-center justify-center">
          <Trello size={16} className="text-white" />
        </div>
        <span className="text-slate-100 font-semibold text-lg">TrelloLite</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}

        {/* Admin section */}
        {user?.role === 'admin' && (
          <>
            <div className="mt-4 mb-2 px-3 text-xs text-slate-500 uppercase tracking-wider font-semibold">
              Admin
            </div>
            <NavLink
              to="/admin/users"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                }`
              }
            >
              <Users size={18} />
              Manage Users
            </NavLink>
          </>
        )}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-slate-700 flex flex-col gap-1">
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isActive
                ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
            }`
          }
        >
          <User size={18} />
          Profile
        </NavLink>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-900/20 transition-colors w-full text-left"
        >
          <LogOut size={18} />
          Log Out
        </button>

        {/* User info */}
        {user && (
          <div className="mt-2 flex items-center gap-3 px-3 py-2">
            <Avatar name={user.username} size="sm" />
            <div className="flex flex-col min-w-0">
              <span className="text-slate-200 text-sm font-medium truncate">{user.username}</span>
              <span className="text-slate-500 text-xs truncate">{user.email}</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
