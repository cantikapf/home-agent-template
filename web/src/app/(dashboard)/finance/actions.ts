"use server";

import { db } from '@/lib/firebase';
import { FieldValue } from 'firebase-admin/firestore';
import { revalidatePath } from 'next/cache';

export async function addExpenseAction(formData: FormData) {
  const amountStr = formData.get('amount');
  const amount = Number(amountStr);
  const category = formData.get('category') as string;
  const description = formData.get('description') as string;

  if (!amount || !category || !description) {
    throw new Error('Semua field harus diisi dengan benar');
  }

  await db.collection('expenses').add({
    amount,
    category,
    description,
    timestamp: FieldValue.serverTimestamp()
  });

  revalidatePath('/finance');
}
