"use client";

import { useState } from 'react';
import { Search } from 'lucide-react';

export default function RecipeClient({ initialRecipes }: { initialRecipes: any[] }) {
  const [search, setSearch] = useState('');

  const filtered = initialRecipes.filter(r => {
    const term = search.toLowerCase();
    const name = r.name?.toLowerCase() || '';
    const ingredients = r.ingredients?.toLowerCase() || '';
    return name.includes(term) || ingredients.includes(term);
  });

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 opacity-50" />
        <input
          type="text"
          placeholder="Cari nama resep atau bahan..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-[var(--background)] border border-[var(--border)] rounded-sm py-2 pl-9 pr-4 text-sm focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.length === 0 ? (
          <div className="col-span-full p-8 text-center border border-[var(--border)] border-dashed rounded-sm">
            <p className="text-sm opacity-50">Resep tidak ditemukan.</p>
          </div>
        ) : (
          filtered.map((r: any) => (
            <div key={r.id} className="bg-[var(--card)] p-5 border border-[var(--border)] rounded-sm space-y-4">
              <h2 className="text-xl font-medium">{r.name}</h2>
              {(r.source_url || r.url) && (
                <a href={r.source_url || r.url} target="_blank" rel="noreferrer" className="text-blue-600 dark:text-blue-500 text-sm hover:underline">
                  Lihat Sumber
                </a>
              )}
              <div className="pt-4 border-t border-[var(--border)] border-dashed">
                <h3 className="text-xs font-semibold opacity-50 uppercase tracking-wider mb-2">Bahan:</h3>
                <p className="text-sm opacity-80 whitespace-pre-wrap font-mono">{r.ingredients || '-'}</p>
              </div>
              <div className="pt-4 border-t border-[var(--border)] border-dashed">
                <h3 className="text-xs font-semibold opacity-50 uppercase tracking-wider mb-2">Langkah:</h3>
                <p className="text-sm opacity-80 whitespace-pre-wrap">{r.steps || '-'}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
