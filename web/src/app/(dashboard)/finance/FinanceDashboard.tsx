"use client";

import React, { useState } from 'react';
import { CreditCard, Plus, Calendar, ArrowRight, Utensils, ShoppingBag, Car, Zap, FileText, PieChart as PieChartIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useRouter, useSearchParams } from 'next/navigation';
import AddExpenseDialog from '@/components/AddExpenseDialog';

const COLORS = ['#6366f1', '#10b981', '#f43f5e', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#64748b'];

const getCategoryIcon = (category: string) => {
  const cat = category.toLowerCase();
  if (cat.includes('makan') || cat.includes('food')) return <Utensils className="w-5 h-5 text-orange-400" />;
  if (cat.includes('belanja') || cat.includes('shop') || cat.includes('grocer')) return <ShoppingBag className="w-5 h-5 text-indigo-400" />;
  if (cat.includes('transport') || cat.includes('gojek') || cat.includes('grab')) return <Car className="w-5 h-5 text-emerald-400" />;
  if (cat.includes('listrik') || cat.includes('tagihan') || cat.includes('air')) return <Zap className="w-5 h-5 text-yellow-400" />;
  return <FileText className="w-5 h-5 text-zinc-400" />;
};

export default function FinanceDashboard({ initialMonth, budget, expenses }: { initialMonth: string, budget: number, expenses: any[] }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedMonth, setSelectedMonth] = useState(initialMonth);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('Semua');

  const uniqueCategories = ['Semua', ...Array.from(new Set(expenses.map(e => e.category || 'Lain-lain'))).sort()];
  
  const filteredExpenses = selectedCategory === 'Semua' 
    ? expenses 
    : expenses.filter(exp => (exp.category || 'Lain-lain') === selectedCategory);
    
  const filteredTotal = filteredExpenses.reduce((acc, curr) => acc + (curr.amount || 0), 0);

  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedMonth(val);
    const params = new URLSearchParams(searchParams.toString());
    params.set('month', val);
    router.push(`?${params.toString()}`);
  };

  const totalExpense = expenses.reduce((acc, curr) => acc + (curr.amount || 0), 0);
  const currentCash = budget; // budget prop now holds the actual current available cash
  const WANTS_CATEGORIES = [
    'hiburan', 'hobi', 'entertainment', 'lifestyle', 
    'pakaian', 'fashion', 'gaya hidup'
  ];

  const WANTS_KEYWORDS = [
    'wants', 'keinginan', 'jajan', 'hiburan', 'hobi', 'entertainment', 'lifestyle', 'rekreasi',
    'kopi', 'coffee', 'latte', 'cappuccino', 'espresso', 'ngopi', 'cafe', 'kafe',
    'juice', 'jus', 'boba', 'matcha', 'tea', 'chatime', 'starbucks', 'fore', 'kenangan', 'point coffee',
    'snack', 'dessert', 'sushi', 'durian', 'pancake', 'cake', 'roti', 'pastry', 
    'ice cream', 'eskrim', 'shopeefood', 'gofood', 'grabfood',
    'baju', 'celana', 'sepatu', 'pakaian', 'outfit', 'executive', 'uniqlo', 'zara', 'h&m',
    'game', 'top-up', 'topup', 'diamond', 'diamonds', 'steam', 'playstation', 
    'bioskop', 'cinema', 'xxi', 'nonton', 'netflix', 'spotify',
    'vikey', 'token api', 'api ai', 'antigravity', 'chatgpt', 'openai', 'claude', 'midjourney',
    'treatment', 'salon', 'spa', 'skincare', 'perawatan'
  ];

  const totalWants = expenses.reduce((acc, curr) => {
    const cat = (curr.category || '').toLowerCase();
    const desc = (curr.description || '').toLowerCase();
    const isCatMatch = WANTS_CATEGORIES.some(c => cat.includes(c));
    const isKwMatch = WANTS_KEYWORDS.some(k => cat.includes(k) || desc.includes(k));
    if (isCatMatch || isKwMatch) {
      return acc + (curr.amount || 0);
    }
    return acc;
  }, 0);
  const wantsPercent = totalExpense > 0 ? (totalWants / totalExpense) * 100 : 0;
  const percentUsed = currentCash > 0 ? Math.min((totalExpense / (currentCash + totalExpense)) * 100, 100) : 0;
  
  let progressColor = "bg-emerald-500";
  if (percentUsed > 90) progressColor = "bg-red-500";
  else if (percentUsed > 75) progressColor = "bg-yellow-500";

  // Aggregate for Pie Chart
  const categoryMap = new Map<string, number>();
  expenses.forEach(exp => {
    const c = exp.category || 'Lain-lain';
    categoryMap.set(c, (categoryMap.get(c) || 0) + exp.amount);
  });
  const pieData = Array.from(categoryMap.entries()).map(([name, value]) => ({ name, value })).sort((a,b) => b.value - a.value);

  // Generate last 6 months for selector
  const generateMonths = () => {
    const opts = [];
    const now = new Date();
    for (let i = 0; i < 6; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const val = d.toISOString().slice(0, 7);
      opts.push({ value: val, label: d.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' }) });
    }
    return opts;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <CreditCard className="w-5 h-5 text-indigo-500" />
          </div>
          <h1 className="text-2xl font-bold">Ringkasan Keuangan</h1>
        </div>
        
        <div className="flex items-center gap-3">
          <select 
            value={selectedMonth} 
            onChange={handleMonthChange}
            className="bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {generateMonths().map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <button 
            onClick={() => setShowAddDialog(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm px-4"
          >
            <Plus className="w-4 h-4" /> <span className="hidden sm:inline">Catat Pengeluaran</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group">
          <h3 className="text-zinc-400 text-sm font-semibold">Cash Tersedia</h3>
          <p className={`text-3xl font-bold mt-2 ${currentCash < 0 ? 'text-red-500' : 'text-emerald-400'}`}>
            Rp {currentCash.toLocaleString('id-ID')}
          </p>
        </div>
        <div className="glass-card p-5 rounded-2xl">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-zinc-400 text-sm font-semibold">Total Pengeluaran</h3>
              <p className="text-3xl font-bold text-red-400 mt-2">Rp {totalExpense.toLocaleString('id-ID')}</p>
            </div>
            <div className="text-right">
              <span className="text-xs text-zinc-500 font-medium">{percentUsed.toFixed(1)}% terpakai</span>
            </div>
          </div>
          
          <div className="mt-4 h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
            <div className={`h-full ${progressColor} transition-all duration-500`} style={{ width: `${Math.min(percentUsed, 100)}%` }}></div>
          </div>
        </div>
        <div className="glass-card p-5 rounded-2xl flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-zinc-400 text-sm font-semibold">Pengeluaran "Wants"</h3>
              <p className="text-3xl font-bold text-yellow-400 mt-2">Rp {totalWants.toLocaleString('id-ID')}</p>
            </div>
            <div className="text-right">
              <span className={`text-xs font-medium ${wantsPercent > 30 ? 'text-red-400' : 'text-zinc-500'}`}>
                {wantsPercent.toFixed(1)}% dari total
              </span>
            </div>
          </div>
          <div className="mt-4 text-xs text-zinc-500">
            *Batas ideal 50/30/20 rule: Max 30%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl lg:col-span-1">
          <div className="flex items-center gap-2 mb-6">
            <PieChartIcon className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white">Distribusi Kategori</h2>
          </div>
          
          {pieData.length > 0 ? (
            <div className="w-full" style={{ height: Math.max(250, 200 + Math.ceil(pieData.length / 2) * 24) }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={COLORS[index % COLORS.length]} 
                        onClick={() => setSelectedCategory(selectedCategory === entry.name ? 'Semua' : entry.name)}
                        className="cursor-pointer hover:opacity-80 transition-opacity outline-none"
                      />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => `Rp ${value.toLocaleString('id-ID')}`}
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                    itemStyle={{ color: '#e4e4e7' }}
                  />
                  <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-zinc-500 text-sm">
              Belum ada data bulan ini
            </div>
          )}
        </div>

        <div className="glass-card p-6 rounded-2xl lg:col-span-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Riwayat Pengeluaran
            </h2>
            <div className="flex items-center gap-3">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-zinc-900/50 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {uniqueCategories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <span className="text-xs text-zinc-500 whitespace-nowrap">
                {filteredExpenses.length} Transaksi
                {selectedCategory !== 'Semua' && ` • Rp ${filteredTotal.toLocaleString('id-ID')}`}
              </span>
            </div>
          </div>
          
          {filteredExpenses.length > 0 ? (
            <div className="space-y-3 max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
              {filteredExpenses.map((exp: any) => (
                <div key={exp.id} className="p-4 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors rounded-xl flex items-center justify-between border border-zinc-800/50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center shrink-0">
                      {getCategoryIcon(exp.category)}
                    </div>
                    <div>
                      <p className="font-medium text-white">{exp.description}</p>
                      <div className="flex items-center gap-2 text-xs text-zinc-400 mt-1">
                        <span className="bg-zinc-800 px-2 py-0.5 rounded-full">{exp.category}</span>
                        <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(exp.timestamp).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  </div>
                  <p className="font-bold text-red-400 whitespace-nowrap">-Rp {exp.amount?.toLocaleString('id-ID')}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-zinc-500">
              <p>Belum ada pengeluaran yang dicatat di bulan ini.</p>
            </div>
          )}
        </div>
      </div>

      <AddExpenseDialog 
        open={showAddDialog}
        onClose={() => setShowAddDialog(false)}
      />
    </div>
  );
}
