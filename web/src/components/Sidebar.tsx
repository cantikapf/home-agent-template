"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Settings, FileText, Brain, FileCode,
  MessageSquare, Clock, BookOpen, X, Zap,
  ChevronLeft, ChevronRight, Bot, Sparkles, KeyRound, Activity,
  Bell, Database, Sun, Moon, Menu, Terminal, Shield,
  CreditCard, Globe, Wrench, ListTodo
} from 'lucide-react';
import { useState } from 'react';
import { useTheme } from 'next-themes';

interface NavSection {
  label: string;
  items: Array<{ href: string; label: string; icon: any }>;
}

const navSections: NavSection[] = [
  {
    label: 'Monitoring & System',
    items: [
      { href: '/', label: 'System Overview', icon: LayoutDashboard },
      { href: '/logs', label: 'Live Logs', icon: FileText },
      { href: '/audit', label: 'Audit Log', icon: Shield },
    ],
  },
  {
    label: 'Home & Finance',
    items: [
      { href: '/finance', label: 'Keuangan', icon: CreditCard },
      { href: '/shopping', label: 'Daftar Belanja', icon: ListTodo },
      { href: '/fridge', label: 'Stok Kulkas', icon: Database },
      { href: '/recipes', label: 'Buku Resep', icon: BookOpen },
    ],
  },
  {
    label: 'Configuration',
    items: [
      { href: '/env-vars', label: 'Env Variables', icon: KeyRound },
      { href: '/agent-md', label: 'Agent Rules', icon: Bot },
      { href: '/maintenance', label: 'Maintenance', icon: Wrench },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  if (pathname === '/login') return null;

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <button
        onClick={() => setMobileOpen(true)}
        className="fixed top-4 left-4 z-50 lg:hidden p-3 rounded-none bg-[var(--card)] border border-[var(--border)] min-w-[44px] min-h-[44px] flex items-center justify-center"
      >
        <Menu className="w-5 h-5" />
      </button>

      <aside className={`
        fixed top-0 left-0 h-full z-50
        flex flex-col
        transition-all duration-0 ease-in-out
        ${collapsed ? 'w-[72px]' : 'w-[260px]'}
        border-r border-[var(--border)]
        bg-[hsl(var(--background))]
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex items-center gap-3 px-5 py-5 border-b border-[var(--border)]">
          <div className="w-9 h-9 rounded-sm bg-black dark:bg-white flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-white dark:text-black" />
          </div>
          {!collapsed && (
            <div className="flex items-center gap-2">
              <div>
                <h1 className="text-lg font-bold text-black dark:text-white">Hermes</h1>
                <p className="text-[10px] text-black/50 dark:text-white/50 -mt-1 uppercase tracking-wider">Admin Dashboard</p>
              </div>
              <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded-none bg-black/10 dark:bg-white/10 text-black dark:text-white border border-[var(--border)] leading-none">
                v0.1
              </span>
            </div>
          )}
          <button onClick={() => setMobileOpen(false)} className="ml-auto lg:hidden p-1 min-w-[44px] min-h-[44px] flex items-center justify-center">
            <X className="w-5 h-5 opacity-50" />
          </button>
        </div>

        <nav className="flex-1 py-4 px-3 overflow-y-auto">
          {navSections.map((section, sIdx) => (
            <div key={section.label} className={`${sIdx > 0 ? 'mt-5' : ''}`}>
              {!collapsed && (
                <p className="px-3 py-1.5 text-[10px] font-semibold opacity-50 uppercase tracking-wider">
                  {section.label}
                </p>
              )}
              <div className="space-y-0.5 mt-1">
                {section.items.map((item) => {
                  const isActive = pathname === item.href ||
                    (item.href !== '/' && pathname.startsWith(item.href));
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className={`
                        relative flex items-center gap-3 px-3 py-2.5 rounded-none
                        min-h-[44px]
                        ${isActive
                          ? 'bg-[var(--card)] font-medium text-black dark:text-white border border-[var(--border)] shadow-sm'
                          : 'opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5 border border-transparent'
                        }
                      `}
                    >
                      <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-500' : ''}`} />
                      {!collapsed && (
                        <span className="text-sm">{item.label}</span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="hidden lg:block px-3 py-2 border-t border-[var(--border)]">
          <div className="flex items-center gap-1">
            <button
              onClick={toggleTheme}
              className="flex items-center justify-center p-2.5 rounded-sm opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5 min-w-[44px] min-h-[44px]"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <div className="flex-1" />
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="flex items-center justify-center p-2.5 rounded-sm opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5 min-w-[44px] min-h-[44px]"
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </aside>

      <div className={`transition-all duration-0 ${collapsed ? 'lg:ml-[72px]' : 'lg:ml-[260px]'}`} />

      <nav className="fixed bottom-0 left-0 right-0 z-40 lg:hidden bg-[hsl(var(--background))] border-t border-[var(--border)] safe-bottom">
        <div className="flex items-center justify-around px-2 py-1.5">
          {[
            { href: '/', label: 'Home', icon: LayoutDashboard },
            { href: '/finance', label: 'Keuangan', icon: CreditCard },
            { href: '/shopping', label: 'Belanja', icon: ListTodo },
            { href: '/fridge', label: 'Kulkas', icon: Database },
            { href: '/recipes', label: 'Resep', icon: BookOpen },
          ].map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center gap-0.5 p-2 min-w-[48px] min-h-[48px] justify-center ${
                  isActive
                    ? 'text-blue-600 dark:text-blue-500'
                    : 'opacity-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
