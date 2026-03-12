import { useState, useCallback } from 'react';
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
  closestCenter,
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import type { Task, TaskStatus } from '../../types';
import { KanbanColumn } from './KanbanColumn';
import { TaskCardOverlay } from './TaskCard';

const STATUSES: TaskStatus[] = ['todo', 'in_progress', 'done'];

interface KanbanBoardProps {
  tasks: Task[];
  onStatusChange: (taskId: number, newStatus: TaskStatus) => Promise<void>;
  onAddTask: (status: TaskStatus) => void;
  onEditTask: (task: Task) => void;
  onDeleteTask: (task: Task) => void;
  isOwner: boolean;
}

export function KanbanBoard({
  tasks,
  onStatusChange,
  onAddTask,
  onEditTask,
  onDeleteTask,
  isOwner,
}: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const getTasksByStatus = useCallback(
    (status: TaskStatus) => tasks.filter((t) => t.status === status),
    [tasks]
  );

  const handleDragStart = ({ active }: DragStartEvent) => {
    const task = tasks.find((t) => t.id === active.id);
    setActiveTask(task ?? null);
  };

  const handleDragEnd = async ({ active, over }: DragEndEvent) => {
    setActiveTask(null);
    if (!over) return;

    const draggedTask = tasks.find((t) => t.id === active.id);
    if (!draggedTask) return;

    // Check if dropped over a column (status id) or another card
    const overId = over.id as string | number;

    // Determine target status
    let targetStatus: TaskStatus | null = null;
    if (STATUSES.includes(overId as TaskStatus)) {
      targetStatus = overId as TaskStatus;
    } else {
      // Dropped over another task — find that task's status
      const overTask = tasks.find((t) => t.id === overId);
      if (overTask) targetStatus = overTask.status;
    }

    if (targetStatus && targetStatus !== draggedTask.status) {
      await onStatusChange(draggedTask.id, targetStatus);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {STATUSES.map((status) => (
          <KanbanColumn
            key={status}
            status={status}
            tasks={getTasksByStatus(status)}
            onAddTask={onAddTask}
            onEditTask={onEditTask}
            onDeleteTask={onDeleteTask}
            isOwner={isOwner}
          />
        ))}
      </div>

      <DragOverlay>
        {activeTask ? <TaskCardOverlay task={activeTask} /> : null}
      </DragOverlay>
    </DndContext>
  );
}
