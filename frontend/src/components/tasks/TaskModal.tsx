import { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input, TextArea, Select } from '../ui/Input';
import { Button } from '../ui/Button';
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskStatus, TaskPriority } from '../../types';

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => Promise<void>;
  task?: Task | null;
  defaultStatus?: TaskStatus;
}

const statusOptions = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
];

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
];

export function TaskModal({ isOpen, onClose, onSubmit, task, defaultStatus = 'todo' }: TaskModalProps) {
  const isEdit = !!task;

  const [form, setForm] = useState({
    title: '',
    description: '',
    status: defaultStatus as string,
    priority: 'medium' as string,
    due_date: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      if (task) {
        setForm({
          title: task.title,
          description: task.description ?? '',
          status: task.status,
          priority: task.priority,
          due_date: task.due_date ?? '',
        });
      } else {
        setForm({
          title: '',
          description: '',
          status: defaultStatus,
          priority: 'medium',
          due_date: '',
        });
      }
      setErrors({});
    }
  }, [isOpen, task, defaultStatus]);

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.title.trim()) e.title = 'Title is required';
    if (form.title.length > 200) e.title = 'Max 200 characters';
    return e;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }

    setLoading(true);
    try {
      const payload: CreateTaskRequest | UpdateTaskRequest = {
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        status: form.status as TaskStatus,
        priority: form.priority as TaskPriority,
        due_date: form.due_date || undefined,
      };
      await onSubmit(payload);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? 'Edit Task' : 'Create Task'}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Title"
          value={form.title}
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          placeholder="Task title..."
          error={errors.title}
          autoFocus
        />
        <TextArea
          label="Description"
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          placeholder="Optional description..."
          rows={3}
        />
        <div className="grid grid-cols-2 gap-3">
          <Select
            label="Status"
            value={form.status}
            onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
            options={statusOptions}
          />
          <Select
            label="Priority"
            value={form.priority}
            onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
            options={priorityOptions}
          />
        </div>
        <Input
          label="Due Date"
          type="date"
          value={form.due_date}
          onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
        />
        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading}>
            {isEdit ? 'Save Changes' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
