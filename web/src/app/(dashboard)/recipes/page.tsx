import { db } from '@/lib/firebase';
import { BookOpen } from 'lucide-react';
import RecipeClient from './RecipeClient';

export const dynamic = 'force-dynamic';

export default async function RecipesPage() {
  const snapshot = await db.collection('recipes').get();
  const recipes = snapshot.docs.map(doc => {
    const data = doc.data();
    for (const key in data) {
      if (data[key] && typeof data[key].toDate === 'function') {
        data[key] = data[key].toDate().toISOString();
      }
    }
    return { id: doc.id, ...data };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 border-b border-[var(--border)] pb-4">
        <div className="w-10 h-10 border border-[var(--border)] bg-[var(--card)] rounded-sm flex items-center justify-center">
          <BookOpen className="w-5 h-5 opacity-70" />
        </div>
        <div>
          <h1 className="text-2xl font-light">Buku Resep</h1>
          <p className="text-xs opacity-50 uppercase tracking-wider mt-1">Total: {recipes.length} Resep</p>
        </div>
      </div>
      
      <RecipeClient initialRecipes={recipes} />
    </div>
  );
}
