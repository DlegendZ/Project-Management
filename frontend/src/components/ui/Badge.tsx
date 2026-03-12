import type { TaskStatus, TaskPriority } from '../../types';

// ─── Status Badge ─────────────────────────────────────────────────────────────

const statusStyles: Record<TaskStatus, string> = {
  todo: 'bg-slate-700 text-slate-300',
  in_progress: 'bg-blue-900/60 text-blue-300',
  done: 'bg-green-900/60 text-green-300',
};

const statusLabels: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  done: 'Done',
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  );
}

// ─── Priority Badge ───────────────────────────────────────────────────────────

const priorityStyles: Record<TaskPriority, string> = {
  low: 'bg-slate-700 text-slate-400',
  medium: 'bg-amber-900/60 text-amber-300',
  high: 'bg-red-900/60 text-red-400',
};

const priorityDot: Record<TaskPriority, string> = {
  low: 'bg-slate-400',
  medium: 'bg-amber-400',
  high: 'bg-red-400',
};

export function PriorityBadge({ priority }: { priority: TaskPriority }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium ${priorityStyles[priority]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${priorityDot[priority]}`} />
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  );
}

// ─── Role Badge ───────────────────────────────────────────────────────────────

export function RoleBadge({ role }: { role: string }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
        role === 'admin' ? 'bg-indigo-900/60 text-indigo-300' : 'bg-slate-700 text-slate-400'
      }`}
    >
      {role}
    </span>
  );
}

// ─── Generic Badge ────────────────────────────────────────────────────────────

interface BadgeProps {
  children: React.ReactNode;
  color?: 'default' | 'green' | 'red' | 'blue' | 'amber';
  className?: string;
}

const colorMap = {
  default: 'bg-slate-700 text-slate-300',
  green: 'bg-green-900/60 text-green-300',
  red: 'bg-red-900/60 text-red-400',
  blue: 'bg-blue-900/60 text-blue-300',
  amber: 'bg-amber-900/60 text-amber-300',
};

export function Badge({ children, color = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colorMap[color]} ${className}`}>
      {children}
    </span>
  );
}
