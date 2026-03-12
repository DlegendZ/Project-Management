import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Calendar, User2, GripVertical, Pencil, Trash2 } from 'lucide-react';
import { format, isPast, parseISO } from 'date-fns';
import type { Task } from '../../types';
import { PriorityBadge } from '../ui/Badge';
import { Avatar } from '../ui/Avatar';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  isOwner: boolean;
}

export function TaskCard({ task, onEdit, onDelete, isOwner }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const isOverdue =
    task.due_date && task.status !== 'done' && isPast(parseISO(task.due_date));

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-slate-900 border border-slate-700 rounded-lg p-3 group hover:border-slate-500 transition-colors"
    >
      {/* Drag handle + actions */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <button
          {...attributes}
          {...listeners}
          className="text-slate-600 hover:text-slate-400 cursor-grab active:cursor-grabbing mt-0.5 flex-shrink-0"
        >
          <GripVertical size={14} />
        </button>
        <p className="text-slate-200 text-sm font-medium flex-1 leading-snug">{task.title}</p>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
          <button
            onClick={() => onEdit(task)}
            className="text-slate-500 hover:text-indigo-400 transition-colors"
          >
            <Pencil size={13} />
          </button>
          {isOwner && (
            <button
              onClick={() => onDelete(task)}
              className="text-slate-500 hover:text-red-400 transition-colors"
            >
              <Trash2 size={13} />
            </button>
          )}
        </div>
      </div>

      {/* Description snippet */}
      {task.description && (
        <p className="text-xs text-slate-500 mb-2 line-clamp-2 ml-5">{task.description}</p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between ml-5 mt-2">
        <div className="flex items-center gap-2">
          <PriorityBadge priority={task.priority} />
          {task.due_date && (
            <span
              className={`flex items-center gap-1 text-xs ${
                isOverdue ? 'text-red-400' : 'text-slate-500'
              }`}
            >
              <Calendar size={11} />
              {format(parseISO(task.due_date), 'MMM d')}
            </span>
          )}
        </div>

        {/* Assignees */}
        {task.assignees && task.assignees.length > 0 && (
          <div className="flex items-center -space-x-1">
            {task.assignees.slice(0, 3).map((u) => (
              <Avatar key={u.id} name={u.username} size="sm" className="border border-slate-800" />
            ))}
            {task.assignees.length > 3 && (
              <span className="text-xs text-slate-500 pl-1.5">+{task.assignees.length - 3}</span>
            )}
          </div>
        )}

        {task.assignees?.length === 0 && (
          <User2 size={13} className="text-slate-600" />
        )}
      </div>
    </div>
  );
}

// ─── Placeholder card while dragging ─────────────────────────────────────────

export function TaskCardOverlay({ task }: { task: Task }) {
  return (
    <div className="bg-slate-900 border border-indigo-500 rounded-lg p-3 shadow-xl rotate-1">
      <p className="text-slate-200 text-sm font-medium">{task.title}</p>
      <div className="mt-2">
        <PriorityBadge priority={task.priority} />
      </div>
    </div>
  );
}
