import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useDroppable } from '@dnd-kit/core';
import { Plus } from 'lucide-react';
import type { Task, TaskStatus } from '../../types';
import { TaskCard } from './TaskCard';

interface KanbanColumnProps {
  status: TaskStatus;
  tasks: Task[];
  onAddTask: (status: TaskStatus) => void;
  onEditTask: (task: Task) => void;
  onDeleteTask: (task: Task) => void;
  isOwner: boolean;
}

const columnConfig: Record<TaskStatus, { label: string; accent: string; dot: string }> = {
  todo: { label: 'To Do', accent: 'border-t-slate-500', dot: 'bg-slate-400' },
  in_progress: { label: 'In Progress', accent: 'border-t-blue-500', dot: 'bg-blue-400' },
  done: { label: 'Done', accent: 'border-t-green-500', dot: 'bg-green-400' },
};

export function KanbanColumn({
  status,
  tasks,
  onAddTask,
  onEditTask,
  onDeleteTask,
  isOwner,
}: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: status });
  const { label, accent, dot } = columnConfig[status];
  const taskIds = tasks.map((t) => t.id);

  return (
    <div className="flex flex-col w-72 flex-shrink-0">
      {/* Column header */}
      <div
        className={`flex items-center justify-between px-3 py-2.5 bg-slate-800 rounded-t-xl border-t-2 ${accent}`}
      >
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${dot}`} />
          <span className="text-slate-200 text-sm font-semibold">{label}</span>
          <span className="text-xs text-slate-500 bg-slate-700 px-1.5 py-0.5 rounded-full">
            {tasks.length}
          </span>
        </div>
        <button
          onClick={() => onAddTask(status)}
          className="text-slate-500 hover:text-indigo-400 transition-colors"
          title="Add task"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Tasks drop zone */}
      <div
        ref={setNodeRef}
        className={`flex-1 min-h-48 flex flex-col gap-2 p-2 bg-slate-800/50 rounded-b-xl border border-t-0 border-slate-700 transition-colors ${
          isOver ? 'bg-indigo-900/20 border-indigo-600/50' : ''
        }`}
      >
        <SortableContext items={taskIds} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onEdit={onEditTask}
              onDelete={onDeleteTask}
              isOwner={isOwner}
            />
          ))}
        </SortableContext>
        {tasks.length === 0 && (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-slate-600 text-xs text-center">Drop tasks here</p>
          </div>
        )}
      </div>
    </div>
  );
}
