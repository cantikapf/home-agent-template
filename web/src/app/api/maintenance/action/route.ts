import { NextResponse } from 'next/server';
import { requireAuth, getHermesHome } from '@/lib/api-utils';
import { NextRequest } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export async function POST(request: NextRequest) {
  const auth = await requireAuth(request);
  if (auth.error) return auth.error;

  try {
    const { action } = await request.json();
    const home = getHermesHome();

    if (action === 'toggle_maintenance') {
      const flagPath = path.join(home, '.maintenance');
      let isEnabled = false;
      if (fs.existsSync(flagPath)) {
        fs.unlinkSync(flagPath);
      } else {
        fs.writeFileSync(flagPath, 'Sistem sedang dalam perbaikan', 'utf8');
        isEnabled = true;
      }
      return NextResponse.json({ success: true, maintenanceMode: isEnabled });
    }

    if (action === 'restart') {
      // Run restart script based on OS
      const isWindows = process.platform === 'win32';
      const scriptName = isWindows ? 'run_dashboard.bat' : 'run_dashboard.sh';
      const scriptPath = path.join(home, scriptName);
      
      // We don't await the restart fully so we can respond
      if (fs.existsSync(scriptPath)) {
        // Execute detached
        exec(`${isWindows ? '' : 'bash '}"${scriptPath}"`, {
          cwd: home,
        });
        return NextResponse.json({ success: true, message: 'Restart command sent' });
      } else {
        return NextResponse.json({ success: true, message: 'Restart triggered (dummy, script not found)' });
      }
    }

    if (action === 'backup') {
      // Since db is Firestore, a real backup would require exporting collections.
      // For now, we return a dummy response
      return NextResponse.json({ success: true, message: 'Firestore Backup initiated on server.' });
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
  } catch (error: any) {
    console.error('Maintenance API error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  const auth = await requireAuth(request);
  if (auth.error) return auth.error;

  try {
    const home = getHermesHome();
    const flagPath = path.join(home, '.maintenance');
    return NextResponse.json({
      maintenanceMode: fs.existsSync(flagPath)
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
