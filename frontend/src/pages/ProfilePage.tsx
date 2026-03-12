import { useState } from 'react';
import { User, Mail, Lock, Save } from 'lucide-react';
import { usersApi } from '../api/users';
import { useAuthStore } from '../store/authStore';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Avatar } from '../components/ui/Avatar';
import { RoleBadge } from '../components/ui/Badge';
import toast from 'react-hot-toast';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';
import { format, parseISO } from 'date-fns';

export function ProfilePage() {
  const { user, setUser } = useAuthStore();

  const [profileForm, setProfileForm] = useState({
    username: user?.username ?? '',
    email: user?.email ?? '',
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm: '',
  });
  const [profileLoading, setProfileLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({});

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    try {
      const updated = await usersApi.updateMe({
        username: profileForm.username.trim(),
        email: profileForm.email.trim(),
      });
      setUser(updated);
      toast.success('Profile updated');
    } catch (err) {
      const axiosErr = err as AxiosError<ApiError>;
      toast.error(axiosErr.response?.data?.error?.message ?? 'Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!passwordForm.current_password) errs.current_password = 'Required';
    if (!passwordForm.new_password) errs.new_password = 'Required';
    if (passwordForm.new_password.length < 8) errs.new_password = 'Min 8 characters';
    if (!/[A-Z]/.test(passwordForm.new_password)) errs.new_password = 'Needs uppercase letter';
    if (!/[0-9]/.test(passwordForm.new_password)) errs.new_password = 'Needs a number';
    if (passwordForm.new_password !== passwordForm.confirm)
      errs.confirm = 'Passwords do not match';
    if (Object.keys(errs).length) { setPasswordErrors(errs); return; }
    setPasswordErrors({});
    setPasswordLoading(true);
    try {
      await usersApi.updateMe({
        new_password: passwordForm.new_password,
        current_password: passwordForm.current_password,
      });
      toast.success('Password updated');
      setPasswordForm({ current_password: '', new_password: '', confirm: '' });
    } catch (err) {
      const axiosErr = err as AxiosError<ApiError>;
      toast.error(axiosErr.response?.data?.error?.message ?? 'Failed to update password');
    } finally {
      setPasswordLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-100 mb-8">Profile Settings</h1>

      {/* Avatar + info */}
      <div className="flex items-center gap-5 mb-8 p-5 bg-slate-800 border border-slate-700 rounded-xl">
        <Avatar name={user.username} size="lg" />
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-100 font-semibold text-lg">{user.username}</h2>
            <RoleBadge role={user.role} />
          </div>
          <p className="text-slate-400 text-sm">{user.email}</p>
          <p className="text-slate-600 text-xs mt-1">
            Member since {format(parseISO(user.created_at), 'MMMM yyyy')}
          </p>
        </div>
      </div>

      {/* Profile form */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-6">
        <h2 className="text-slate-100 font-semibold mb-4 flex items-center gap-2">
          <User size={16} className="text-indigo-400" /> Account Info
        </h2>
        <form onSubmit={handleProfileSave} className="flex flex-col gap-4">
          <Input
            label="Username"
            value={profileForm.username}
            onChange={(e) => setProfileForm((f) => ({ ...f, username: e.target.value }))}
            icon={<User size={15} />}
          />
          <Input
            label="Email"
            type="email"
            value={profileForm.email}
            onChange={(e) => setProfileForm((f) => ({ ...f, email: e.target.value }))}
            icon={<Mail size={15} />}
          />
          <div className="flex justify-end">
            <Button type="submit" loading={profileLoading} icon={<Save size={14} />}>
              Save Changes
            </Button>
          </div>
        </form>
      </div>

      {/* Password form */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h2 className="text-slate-100 font-semibold mb-4 flex items-center gap-2">
          <Lock size={16} className="text-indigo-400" /> Change Password
        </h2>
        <form onSubmit={handlePasswordSave} className="flex flex-col gap-4">
          <Input
            label="Current Password"
            type="password"
            value={passwordForm.current_password}
            onChange={(e) => setPasswordForm((f) => ({ ...f, current_password: e.target.value }))}
            error={passwordErrors.current_password}
            icon={<Lock size={15} />}
          />
          <Input
            label="New Password"
            type="password"
            placeholder="Min 8 chars, upper + lower + number"
            value={passwordForm.new_password}
            onChange={(e) => setPasswordForm((f) => ({ ...f, new_password: e.target.value }))}
            error={passwordErrors.new_password}
            icon={<Lock size={15} />}
          />
          <Input
            label="Confirm New Password"
            type="password"
            value={passwordForm.confirm}
            onChange={(e) => setPasswordForm((f) => ({ ...f, confirm: e.target.value }))}
            error={passwordErrors.confirm}
            icon={<Lock size={15} />}
          />
          <div className="flex justify-end">
            <Button type="submit" loading={passwordLoading} icon={<Save size={14} />}>
              Update Password
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
