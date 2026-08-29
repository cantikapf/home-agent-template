import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import path from 'path';
import fs from 'fs';

if (!getApps().length) {
  try {
    const defaultPath = path.join(process.cwd(), '../firebase-credentials.json');
    const fallbackPath = path.join(process.cwd(), 'firebase-credentials.json');
    const keyPath = process.env.FIREBASE_KEY_PATH || (fs.existsSync(defaultPath) ? defaultPath : fallbackPath);
    
    if (fs.existsSync(keyPath)) {
      const serviceAccount = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
      initializeApp({
        credential: cert(serviceAccount)
      });
    } else {
      console.warn('Firebase key file not found at', keyPath);
    }
  } catch (error) {
    console.error('Firebase initialization error', error);
  }
}

export const db = getFirestore();
