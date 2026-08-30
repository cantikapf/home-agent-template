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
  const [filterWantsOnly, setFilterWantsOnly] = useState(false);

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

  const isWantsExpense = (exp: { category?: string; description?: string }) => {
    const cat = (exp.category || '').toLowerCase();
    const desc = (exp.description || '').toLowerCase();
    const isCatMatch = WANTS_CATEGORIES.some(c => cat.includes(c));
    const isKwMatch = WANTS_KEYWORDS.some(k => cat.includes(k) || desc.includes(k));
    return isCatMatch || isKwMatch;
  };

  const uniqueCategories = ['Semua', ...Array.from(new Set(expenses.map(e => e.category || 'Lain-lain'))).sort()];
  
  // Filter berdasarkan Kategori dan/atau Wants Only
  const filteredExpenses = expenses.filter(exp => {
    const matchCategory = selectedCategory === 'Semua' || (exp.category || 'Lain-lain') === selectedCategory;
    const matchWants = !filterWantsOnly || isWantsExpense(exp);
    return matchCategory && matchWants;
  });
    
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

  const totalWants = expenses.reduce((acc, curr) => {
    if (isWantsExpense(curr)) {
      return acc + (curr.amount || 0);
    }
    return acc;
  }, 0);

  const totalNeeds = Math.max(0, totalExpense - totalWants);
  const wantsPercent = totalExpense > 0 ? (totalWants / totalExpense) * 100 : 0;
  const needsPercent = totalExpense > 0 ? (totalNeeds / totalExpense) * 100 : 0;
  const wantsCount = expenses.filter(e => isWantsExpense(e)).length;

  const percentUsed = currentCash > 0 ? Math.min((totalExpense / (currentCash + totalExpense)) * 100, 100) : 0;
  
  let progressColor = "bg-emerald-500";
  if (percentUsed > 90) progressColor = "bg-red-500";
  else if (percentUsed > 75) progressColor = "bg-yellow-500";

  // Batas ideal Wants (30% dari Total Pengeluaran)
  const maxIdealWants = totalExpense * 0.3;
  const excessWants = Math.max(0, totalWants - maxIdealWants);

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
      
      {/* Top 3 Metric Cards */}
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

        {/* Ide 1 & 3: Interactive Wants Card with 30% Threshold Progress Bar */}
        <div 
          onClick={() => setFilterWantsOnly(!filterWantsOnly)}
          className={`glass-card p-5 rounded-2xl flex flex-col justify-between cursor-pointer transition-all duration-300 relative group ${
            filterWantsOnly 
              ? 'ring-2 ring-amber-500/60 bg-amber-500/5 shadow-lg shadow-amber-500/10' 
              : 'hover:border-zinc-700/80 hover:bg-zinc-900/70'
          }`}
          title="Klik untuk memfilter transaksi khusus pengeluaran Wants"
        >
          <div>
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-2">
                <h3 className="text-zinc-400 text-sm font-semibold">Pengeluaran "Wants"</h3>
                {filterWantsOnly && (
                  <span className="bg-amber-500/20 text-amber-300 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-amber-500/30 animate-pulse">
                    Aktif
                  </span>
                )}
              </div>
              <div className="text-right">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-md ${
                  wantsPercent > 30 
                    ? 'bg-red-500/15 text-red-400 border border-red-500/20' 
                    : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                }`}>
                  {wantsPercent.toFixed(1)}% / 30%
                </span>
              </div>
            </div>

            <p className="text-3xl font-bold text-yellow-400 mt-2">Rp {totalWants.toLocaleString('id-ID')}</p>
          </div>

          {/* Ide 3: Progress Bar with 30% Target Marker */}
          <div className="mt-4 space-y-2">
            <div className="relative h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
              {/* Dynamic Fill Bar */}
              <div 
                className={`h-full transition-all duration-500 ${
                  wantsPercent > 30 ? 'bg-gradient-to-r from-amber-400 to-rose-500' : 'bg-emerald-400'
                }`}
                style={{ width: `${Math.min(wantsPercent, 100)}%` }}
              />
              {/* 30% Threshold Marker Line */}
              <div 
                className="absolute top-0 bottom-0 w-0.5 bg-white/70 z-10 shadow-[0_0_4px_rgba(255,255,255,0.8)]"
                style={{ left: '30%' }}
                title="Ambang batas 30%"
              />
            </div>

            <div className="flex items-center justify-between text-[11px]">
              <span className={wantsPercent > 30 ? 'text-rose-400 font-medium' : 'text-emerald-400'}>
                {wantsPercent > 30 
                  ? `⚠️ Melebihi batas ideal (+Rp ${excessWants.toLocaleString('id-ID')})`
                  : `🟢 Porsi aman (≤ 30%)`}
              </span>
              <span className="text-zinc-500 group-hover:text-amber-300 transition-colors flex items-center gap-1">
                {filterWantsOnly ? 'Tampilkan Semua' : 'Klik untuk filter'} &rarr;
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Ide 5: Comparison Split Bar "Needs vs Wants" (50/30/20 Rule) */}
      <div className="glass-card p-4 sm:p-5 rounded-2xl border border-zinc-800/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">Rasio Alokasi 50/30/20</span>
            <span className="text-zinc-600">•</span>
            <span className="text-xs text-zinc-500">Needs (Kebutuhan) vs Wants (Keinginan)</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-indigo-500"></div>
              <span className="text-zinc-400 font-medium">Needs: {needsPercent.toFixed(1)}%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400"></div>
              <span className="text-zinc-400 font-medium">Wants: {wantsPercent.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Dual Segment Stacked Bar */}
        <div className="h-3 w-full bg-zinc-800 rounded-full overflow-hidden flex p-0.5 gap-0.5">
          <div 
            className="h-full bg-indigo-500 rounded-l-full transition-all duration-500" 
            style={{ width: `${needsPercent}%` }}
            title={`Needs: Rp ${totalNeeds.toLocaleString('id-ID')} (${needsPercent.toFixed(1)}%)`}
          />
          <div 
            className={`h-full rounded-r-full transition-all duration-500 ${
              wantsPercent > 30 ? 'bg-rose-500' : 'bg-amber-400'
            }`}
            style={{ width: `${wantsPercent}%` }}
            title={`Wants: Rp ${totalWants.toLocaleString('id-ID')} (${wantsPercent.toFixed(1)}%)`}
          />
        </div>

        <div className="flex items-center justify-between text-xs text-zinc-500 mt-2.5 pt-2 border-t border-zinc-800/40">
          <span>Kebutuhan: <strong className="text-indigo-400">Rp {totalNeeds.toLocaleString('id-ID')}</strong></span>
          <span>Keinginan: <strong className={wantsPercent > 30 ? 'text-rose-400' : 'text-amber-400'}>Rp {totalWants.toLocaleString('id-ID')}</strong> ({wantsCount} transaksi)</span>
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
                    formatter={(value: any) => `Rp ${Number(value || 0).toLocaleString('id-ID')}`}
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
          <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-4 gap-3">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Riwayat Pengeluaran
              </h2>
              {/* Ide 1: Pill Toggle Filter Khusus Wants */}
              <div className="flex items-center gap-1.5 mt-2">
                <button
                  onClick={() => setFilterWantsOnly(false)}
                  className={`text-xs px-2.5 py-1 rounded-lg transition-colors font-medium ${
                    !filterWantsOnly 
                      ? 'bg-zinc-800 text-white border border-zinc-700' 
                      : 'text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  Semua ({expenses.length})
                </button>
                <button
                  onClick={() => setFilterWantsOnly(true)}
                  className={`text-xs px-2.5 py-1 rounded-lg transition-colors font-medium flex items-center gap-1 ${
                    filterWantsOnly 
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' 
                      : 'text-zinc-500 hover:text-amber-300'
                  }`}
                >
                  🛍️ Khusus Wants ({wantsCount})
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2 sm:self-start">
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
                {(selectedCategory !== 'Semua' || filterWantsOnly) && ` • Rp ${filteredTotal.toLocaleString('id-ID')}`}
              </span>
            </div>
          </div>
          
          {filteredExpenses.length > 0 ? (
            <div className="space-y-3 max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
              {filteredExpenses.map((exp: any) => {
                const isWants = isWantsExpense(exp);
                return (
                  <div key={exp.id} className="p-4 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors rounded-xl flex items-center justify-between border border-zinc-800/50">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center shrink-0">
                        {getCategoryIcon(exp.category)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-white">{exp.description}</p>
                          {/* Ide 2: Visual Badge/Chip "🛍️ Wants" */}
                          {isWants && (
                            <span className="bg-amber-500/15 text-amber-300 border border-amber-500/25 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide flex items-center gap-1 shrink-0">
                              🛍️ Wants
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-zinc-400 mt-1">
                          <span className="bg-zinc-800 px-2 py-0.5 rounded-full">{exp.category}</span>
                          <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(exp.timestamp).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                      </div>
                    </div>
                    <p className={`font-bold whitespace-nowrap ${isWants ? 'text-amber-400' : 'text-red-400'}`}>
                      -Rp {exp.amount?.toLocaleString('id-ID')}
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-zinc-500">
              <p>
                {filterWantsOnly 
                  ? 'Tidak ada pengeluaran kategori Wants pada filter ini.' 
                  : 'Belum ada pengeluaran yang dicatat di bulan ini.'}
              </p>
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
