import { db } from '@/lib/firebase';
import { Database } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default async function FridgePage() {
  const snapshot = await db.collection('inventory').get();
  const items = snapshot.docs.map(doc => ({ id: doc.id, ...(doc.data() as any) }));

  const categorizedItems = items.reduce((acc, item) => {
    const cat = item.category || 'Lainnya';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <Database className="w-5 h-5 text-indigo-500" />
        </div>
        <h1 className="text-2xl font-bold">Stok Kulkas & Dapur</h1>
      </div>
      
      {Object.keys(categorizedItems).length === 0 ? (
        <div className="glass-card p-6 rounded-2xl">
          <p className="text-zinc-500 text-center py-4">Kulkas kosong!</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Object.entries(categorizedItems).map(([category, catItems]) => (
            <div key={category} className="glass-card p-6 rounded-2xl h-fit">
              <h2 className="text-lg font-semibold mb-4 text-indigo-500 dark:text-indigo-400 border-b border-zinc-200 dark:border-zinc-800 pb-2">{category}</h2>
              <ul className="space-y-2">
                {catItems.map((item: any) => (
                  <li key={item.id} className="p-3 bg-zinc-50 dark:bg-zinc-900/50 rounded-lg flex items-center justify-between border border-zinc-100 dark:border-zinc-800/50">
                    <div>
                      <p className="font-medium text-zinc-900 dark:text-white capitalize">{item.item || item.id}</p>
                      <p className="text-sm text-zinc-500 dark:text-zinc-400">Sisa: {item.quantity} {item.unit}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
