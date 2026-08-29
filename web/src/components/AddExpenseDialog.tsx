"use client";

import { X } from 'lucide-react';
import { useState } from 'react';
import { addExpenseAction } from '@/app/(dashboard)/finance/actions';

interface AddExpenseDialogProps {
  open: boolean;
  onClose: () => void;
}

export default function AddExpenseDialog({ open, onClose }: AddExpenseDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!open) return null;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError('');
    const formData = new FormData(e.currentTarget);
    try {
      await addExpenseAction(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Terjadi kesalahan');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="p-6 max-w-md w-full animate-fade-in relative z-10 rounded-2xl border dark:border-zinc-700/50 border-zinc-200 dark:bg-zinc-900 bg-white shadow-2xl shadow-black/50 dark:shadow-black/70">
        <button onClick={onClose} className="absolute top-4 right-4 dark:text-zinc-500 text-zinc-400 dark:hover:text-zinc-300 hover:text-zinc-700 transition-colors">
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-lg font-semibold dark:text-zinc-100 text-zinc-900 mb-4">Catat Pengeluaran</h3>
        
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-zinc-300 text-zinc-700">Nominal (Rp)</label>
            <input 
              type="number" 
              name="amount" 
              required
              className="w-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Contoh: 50000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-zinc-300 text-zinc-700">Kategori</label>
            <select 
              name="category"
              className="w-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="Makan & Minum">Makan & Minum</option>
              <option value="Transportasi">Transportasi</option>
              <option value="Belanja Bulanan">Belanja Bulanan</option>
              <option value="Tagihan & Utilitas">Tagihan & Utilitas</option>
              <option value="Hiburan / Keinginan">Hiburan / Keinginan</option>
              <option value="Lain-lain">Lain-lain</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-zinc-300 text-zinc-700">Deskripsi</label>
            <input 
              type="text" 
              name="description"
              required
              className="w-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Contoh: Makan siang nasi padang"
            />
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 rounded-xl text-sm font-medium dark:text-zinc-400 text-zinc-600 dark:hover:text-zinc-200 hover:text-zinc-800 dark:hover:bg-zinc-800/50 hover:bg-zinc-200/50 transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-xl text-sm font-medium text-white transition-all bg-gradient-to-r from-indigo-500 to-violet-500 hover:opacity-90 disabled:opacity-50"
            >
              {loading ? 'Menyimpan...' : 'Simpan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
