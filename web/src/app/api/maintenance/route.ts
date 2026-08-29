import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { getHermesHome } from '@/lib/api-utils';

export async function GET() {
  try {
    const home = getHermesHome();
    const updateCheckPath = path.join(home, '.update_check');
    
    let lastCheck = new Date().toISOString();
    
    if (fs.existsSync(updateCheckPath)) {
      const stats = fs.statSync(updateCheckPath);
      lastCheck = stats.mtime.toISOString();
    }
    
    return NextResponse.json({
      lastCheck: lastCheck,
      autoUpdateStatus: 'enabled'
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
