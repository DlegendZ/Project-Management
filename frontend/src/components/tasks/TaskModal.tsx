import { useState, useEffect } from "react";
import { Modal } from "../ui/Modal";
import { Input, TextArea, Select } from "../ui/Input";
import { Button } from "../ui/Button";
import { Avatar } from "../ui/Avatar";
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskStatus,
  TaskPriority,
  AssigneeInfo,
  User,
} from "../../types";

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => Promise<void>;
  task?: Task | null;
  defaultStatus?: TaskStatus;
  members?: AssigneeInfo[];
  currentUser?: User | null;
  projectOwnerId?: number;
}

const statusOptions = [
  { value: "todo", label: "To Do" },
  { value: "in_progress", label: "In Progress" },
  { value: "done", label: "Done" },
];

const priorityOptions = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

export function TaskModal({
  isOpen,
  onClose,
  onSubmit,
  task,
  defaultStatus = "todo",
  members = [],
  currentUser = null,
  projectOwnerId = undefined,
}: TaskModalProps) {
  const isEdit = !!task;
  const isProjectOwner = currentUser && projectOwnerId
    ? currentUser.id === projectOwnerId
    : false;
  const isTaskCreator = isEdit && task && currentUser
    ? task.created_by === currentUser.id
    : false;
  const isUserAssigned = isEdit && task && currentUser
    ? task.assignees?.some((a) => a.id === currentUser.id) ?? false
    : true;
  const authorizationError =
    isEdit && !isUserAssigned && !isTaskCreator && !isProjectOwner
      ? "Only the task assignee, creator, or project owner can edit this task"
      : null;

  const [form, setForm] = useState({
    title: "",
    description: "",
    status: defaultStatus as string,
    priority: "medium" as string,
    due_date: "",
    assignee_ids: [] as number[],
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      if (task) {
        setForm({
          title: task.title,
          description: task.description ?? "",
          status: task.status,
          priority: task.priority,
          due_date: task.due_date ?? "",
          assignee_ids: task.assignees?.map((a) => a.id) ?? [],
        });
      } else {
        setForm({
          title: "",
          description: "",
          status: defaultStatus,
          priority: "medium",
          due_date: "",
          assignee_ids: [],
        });
      }
      setErrors({});
    }
  }, [isOpen, task, defaultStatus]);

  const toggleAssignee = (id: number) => {
    setForm((f) => ({
      ...f,
      assignee_ids: f.assignee_ids.includes(id)
        ? f.assignee_ids.filter((x) => x !== id)
        : [...f.assignee_ids, id],
    }));
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.title.trim()) e.title = "Title is required";
    if (form.title.length > 200) e.title = "Max 200 characters";

    if (form.due_date) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const selectedDate = new Date(form.due_date);
      if (selectedDate < today) {
        e.due_date = "Due date cannot be in the past";
      }
    }
    return e;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }

    setLoading(true);
    try {
      const payload: CreateTaskRequest | UpdateTaskRequest = {
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        status: form.status as TaskStatus,
        priority: form.priority as TaskPriority,
        due_date: form.due_date || undefined,
        assignee_ids: form.assignee_ids,
      };
      await onSubmit(payload);
      onClose();
    } catch (error) {
      console.error("Failed to submit task:", error);
      // Don't close modal on error, let user retry
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Task" : "Create Task"}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {authorizationError && (
          <div className="p-3 bg-red-950 border border-red-800 rounded text-red-200 text-sm">
            {authorizationError}
          </div>
        )}
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
          onChange={(e) =>
            setForm((f) => ({ ...f, description: e.target.value }))
          }
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
            onChange={(e) =>
              setForm((f) => ({ ...f, priority: e.target.value }))
            }
            options={priorityOptions}
          />
        </div>
        <Input
          label="Due Date"
          type="date"
          value={form.due_date}
          onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
          error={errors.due_date}
        />

        {/* Assignees — shown only when the project has members */}
        {members.length > 0 && (
          <div className="flex flex-col gap-2">
            <label className="text-sm text-slate-300 font-medium">
              Assignees
            </label>
            <div className="flex flex-wrap gap-2">
              {members.map((m) => {
                const selected = form.assignee_ids.includes(m.id);
                return (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => toggleAssignee(m.id)}
                    className={`flex items-center gap-1.5 pl-1 pr-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${
                      selected
                        ? "bg-indigo-600 border-indigo-500 text-white"
                        : "bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    <Avatar name={m.username} size="sm" />
                    {m.username}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            loading={loading}
            disabled={!!authorizationError}
          >
            {isEdit ? "Save Changes" : "Create Task"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
