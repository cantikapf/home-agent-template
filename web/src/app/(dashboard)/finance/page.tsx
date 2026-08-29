import { db } from '@/lib/firebase';
import FinanceDashboard from './FinanceDashboard';

export const dynamic = 'force-dynamic';

export default async function FinancePage(props: { searchParams: Promise<{ month?: string }> }) {
  const searchParams = await props.searchParams;
  
  // Ambil bulan dari parameter URL (misal: ?month=2026-08), default ke bulan saat ini
  const month = searchParams?.month || new Date().toISOString().slice(0, 7);
  
  // Dapatkan limit awal & akhir bulan untuk query Firebase
  const [yearStr, monthStr] = month.split('-');
  const startOfMonth = new Date(parseInt(yearStr), parseInt(monthStr) - 1, 1);
  const endOfMonth = new Date(parseInt(yearStr), parseInt(monthStr), 1);
  
  // Ambil data Cash (aset liquid) sebagai budget bulan ini
  const assetsSnapshot = await db.collection('assets').get();
  let budget = 0;
  assetsSnapshot.docs.forEach(doc => {
    const data = doc.data();
    const type = (data.type || '').toLowerCase();
    if (['liquid', 'balance', 'tunai'].includes(type)) {
      budget += (data.amount || 0);
    }
  });
  
  // Ambil data pengeluaran HANYA di bulan tersebut, diurutkan terbaru
  const snapshot = await db.collection('expenses')
    .where('timestamp', '>=', startOfMonth)
    .where('timestamp', '<', endOfMonth)
    .orderBy('timestamp', 'desc')
    .get();
    
  // Serialize data (hapus object kompleks agar bisa dikirim ke Client Component)
  const expenses = snapshot.docs.map(doc => {
    const data = doc.data();
    return {
      id: doc.id,
      amount: data.amount || 0,
      category: data.category || 'Lain-lain',
      description: data.description || '',
      // Konversi Timestamp firebase ke string ISO
      timestamp: data.timestamp?.toDate().toISOString() || new Date().toISOString(),
    };
  });

  return (
    <FinanceDashboard 
      initialMonth={month} 
      budget={budget} 
      expenses={expenses} 
    />
  );
}
