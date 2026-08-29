"use client";

import { useState, useEffect } from 'react';
import Badge from '@/components/Badge';
import { Wrench, Database, Power, AlertTriangle, Cpu, HardDrive, Download, RefreshCw, Server, Activity } from 'lucide-react';

export default function MaintenancePage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' | 'info' } | null>(null);

  useEffect(() => {
    fetchStats();
    fetchMaintenanceMode();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/system/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const fetchMaintenanceMode = async () => {
    try {
      const res = await fetch('/api/maintenance/action');
      if (res.ok) {
        const data = await res.json();
        setMaintenanceMode(data.maintenanceMode);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const performAction = async (action: string) => {
    setActionLoading(action);
    setMessage(null);
    try {
      const res = await fetch('/api/maintenance/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();
      
      if (res.ok) {
        setMessage({ text: data.message || 'Aksi berhasil', type: 'success' });
        if (action === 'toggle_maintenance') {
          setMaintenanceMode(data.maintenanceMode);
        }
      } else {
        setMessage({ text: data.error || 'Aksi gagal', type: 'error' });
      }
    } catch (e: any) {
      setMessage({ text: e.message || 'Terjadi kesalahan jaringan', type: 'error' });
    }
    setActionLoading(null);
    
    setTimeout(() => setMessage(null), 5000);
  };

  if (loading && !stats) {
    return <div className="flex items-center justify-center h-64"><p className="text-zinc-500">Memuat status sistem...</p></div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold dark:text-zinc-100 text-zinc-900 flex items-center gap-3">
            <Wrench className="w-7 h-7 text-indigo-400" />
            System Maintenance
          </h1>
          <p className="text-sm text-zinc-500 mt-1">Pantau dan kelola layanan Home Agent.</p>
        </div>
        <div className="flex items-center gap-3">
          {message && (
            <Badge variant={message.type}>{message.text}</Badge>
          )}
          {maintenanceMode && (
            <Badge variant="warning">Maintenance Mode Aktif</Badge>
          )}
        </div>
      </div>

      {/* System Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* CPU */}
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
            <Cpu className="w-6 h-6 text-blue-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-zinc-500 mb-1">CPU Load</p>
            <div className="flex items-end justify-between">
              <h3 className="text-2xl font-bold dark:text-zinc-100 text-zinc-900">
                {stats?.cpu?.percent || 0}%
              </h3>
              <span className="text-xs text-zinc-500 pb-1">{stats?.cpu?.cores || 1} Cores</span>
            </div>
            <div className="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-1.5 mt-2">
              <div 
                className="bg-blue-400 h-1.5 rounded-full" 
                style={{ width: `${Math.min(100, stats?.cpu?.percent || 0)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Memory */}
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
            <Activity className="w-6 h-6 text-emerald-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-zinc-500 mb-1">Memory (RAM)</p>
            <div className="flex items-end justify-between">
              <h3 className="text-2xl font-bold dark:text-zinc-100 text-zinc-900">
                {stats?.memory?.percent || 0}%
              </h3>
              <span className="text-xs text-zinc-500 pb-1">
                {Math.round((stats?.memory?.used || 0) / 1024 / 1024 / 1024 * 10) / 10}GB / {Math.round((stats?.memory?.total || 1) / 1024 / 1024 / 1024 * 10) / 10}GB
              </span>
            </div>
            <div className="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-1.5 mt-2">
              <div 
                className="bg-emerald-400 h-1.5 rounded-full" 
                style={{ width: `${Math.min(100, stats?.memory?.percent || 0)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Disk */}
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center flex-shrink-0">
            <HardDrive className="w-6 h-6 text-violet-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-zinc-500 mb-1">Storage</p>
            <div className="flex items-end justify-between">
              <h3 className="text-2xl font-bold dark:text-zinc-100 text-zinc-900">
                {stats?.disk?.percent || 0}%
              </h3>
            </div>
            <div className="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-1.5 mt-2">
              <div 
                className="bg-violet-400 h-1.5 rounded-full" 
                style={{ width: `${Math.min(100, stats?.disk?.percent || 0)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Database & Backup */}
        <div className="glass-card p-5">
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold dark:text-zinc-100 text-zinc-900">Database & Backup</h2>
          </div>
          <p className="text-sm text-zinc-500 mb-6">
            Mencadangkan data Firestore dan file konfigurasi. Backup disarankan sebelum melakukan update.
          </p>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => performAction('backup')}
              disabled={actionLoading === 'backup'}
              className="w-full px-4 py-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 font-medium text-sm hover:bg-indigo-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {actionLoading === 'backup' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              {actionLoading === 'backup' ? 'Memproses...' : 'Backup Database'}
            </button>
          </div>
        </div>

        {/* Service Controls */}
        <div className="glass-card p-5">
          <div className="flex items-center gap-3 mb-4">
            <Server className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold dark:text-zinc-100 text-zinc-900">Service Controls</h2>
          </div>
          <p className="text-sm text-zinc-500 mb-6">
            Kontrol operasi daemon backend Home Agent.
          </p>
          <div className="flex flex-col gap-3">
            <button
              onClick={() => performAction('restart')}
              disabled={actionLoading === 'restart'}
              className="w-full px-4 py-2.5 rounded-xl bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium text-sm hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {actionLoading === 'restart' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
              {actionLoading === 'restart' ? 'Restarting...' : 'Restart Agent'}
            </button>
            
            <button
              onClick={() => performAction('toggle_maintenance')}
              disabled={actionLoading === 'toggle_maintenance'}
              className={`w-full px-4 py-2.5 rounded-xl font-medium text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50 ${
                maintenanceMode
                  ? 'bg-amber-500/20 text-amber-500 hover:bg-amber-500/30'
                  : 'border border-amber-500/50 text-amber-500 hover:bg-amber-500/10'
              }`}
            >
              {actionLoading === 'toggle_maintenance' ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <AlertTriangle className="w-4 h-4" />
              )}
              {maintenanceMode ? 'Matikan Maintenance Mode' : 'Nyalakan Maintenance Mode'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
