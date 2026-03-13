import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Trello } from 'lucide-react';
import { authApi } from '../api/auth';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import toast from 'react-hot-toast';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

export function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.username.trim()) e.username = 'Username is required';
    if (form.username.length < 3) e.username = 'Min 3 characters';
    if (!/^[a-zA-Z0-9_ ]+$/.test(form.username)) e.username = 'Alphanumeric, underscores, and spaces only';
    if (!form.email) e.email = 'Email is required';
    if (!form.password) e.password = 'Password is required';
    if (form.password.length < 8) e.password = 'Min 8 characters';
    if (!/[A-Z]/.test(form.password)) e.password = 'Must contain an uppercase letter';
    if (!/[a-z]/.test(form.password)) e.password = 'Must contain a lowercase letter';
    if (!/[0-9]/.test(form.password)) e.password = 'Must contain a number';
    return e;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    try {
      await authApi.register(form);
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (err) {
      const axiosErr = err as AxiosError<ApiError>;
      const msg = axiosErr.response?.data?.error?.message ?? 'Registration failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mb-3">
            <Trello size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Create an account</h1>
          <p className="text-slate-400 mt-1 text-sm">Join TrelloLite today</p>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Username"
              placeholder="yourname"
              value={form.username}
              onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
              error={errors.username}
              icon={<User size={16} />}
              autoComplete="username"
            />
            <Input
              label="Email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              error={errors.email}
              icon={<Mail size={16} />}
              autoComplete="email"
            />
            <Input
              label="Password"
              type="password"
              placeholder="Min 8 chars, upper + lower + number"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              error={errors.password}
              icon={<Lock size={16} />}
              autoComplete="new-password"
            />
            <Button type="submit" loading={loading} className="mt-2 w-full" size="lg">
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-slate-400 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
