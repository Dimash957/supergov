import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const backend = path.join(root, 'backend');
const win = process.platform === 'win32';
const pyName = win ? 'python.exe' : 'python';

const candidates = [
  path.join(root, '.venv', win ? 'Scripts' : 'bin', pyName),
  path.join(root, 'backend', 'venv', win ? 'Scripts' : 'bin', pyName),
];

const python = candidates.find((p) => existsSync(p));
if (!python) {
  console.error(
    'Не найден Python в .venv или backend\\venv. Создайте venv и: pip install -r backend/requirements.txt',
  );
  process.exit(1);
}

const child = spawn(
  python,
  ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'],
  { cwd: backend, stdio: 'inherit', shell: false },
);

child.on('exit', (code) => process.exit(code ?? 0));
