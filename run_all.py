"""
run_all.py

Arranca el backend FastAPI (uvicorn) y un servidor estático para el frontend
Uso:
    python run_all.py

Requisitos:
- Tener instalado Python 3.7+
- Instalar dependencias si aún no lo hiciste: `pip install -r requirements.txt`

El script intentará ejecutar:
- `uvicorn backend.app:app --host 0.0.0.0 --port 5000`
- `python -m http.server 8080` dentro de la carpeta `frontend`

Ambos procesos se ejecutan en segundo plano; presiona Ctrl+C para detenerlos.
"""

import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_MODULE = 'backend.app:app'
BACKEND_PORT = 5000
FRONTEND_DIR = os.path.join(ROOT, 'frontend')
FRONTEND_PORT = 8080


def check_command(cmd_name):
    return shutil.which(cmd_name) is not None


def main():
    print('\n=== Run All: Backend + Frontend ===\n')

    # Check uvicorn
    if not check_command('uvicorn'):
        print('Advertencia: no se encontró `uvicorn` en PATH.')
        print('Si no lo has instalado, instala dependencias:')
        print('  pip install -r requirements.txt')
        print()

    # Start backend
    backend_cmd = ['uvicorn', BACKEND_MODULE, '--host', '0.0.0.0', '--port', str(BACKEND_PORT), '--reload']
    print('Iniciando backend: ', ' '.join(backend_cmd))
    try:
        backend_proc = subprocess.Popen(backend_cmd, cwd=ROOT)
    except FileNotFoundError:
        print('Error: comando `uvicorn` no encontrado. Asegúrate de instalar uvicorn (pip install uvicorn[standard])')
        backend_proc = None

    # Start frontend static server
    if not os.path.isdir(FRONTEND_DIR):
        print(f'No se encontró la carpeta frontend en {FRONTEND_DIR}. Asegúrate de que exista.')
        frontend_proc = None
    else:
        # Use same python executable to start http.server
        py = sys.executable
        frontend_cmd = [py, '-m', 'http.server', str(FRONTEND_PORT)]
        print(f'Iniciando servidor estático para frontend en {FRONTEND_DIR}: {py} -m http.server {FRONTEND_PORT}')
        frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

    print('\nEndpoints disponibles:')
    print(f'  Backend API: http://localhost:{BACKEND_PORT}/defaults')
    print(f'  Frontend UI: http://localhost:{FRONTEND_PORT}/index.html')
    print('\nPresiona Ctrl+C para detener ambos procesos.')

    try:
        # Simple loop to show processes are running
        while True:
            time.sleep(1)
            if backend_proc and backend_proc.poll() is not None:
                print('\nEl proceso backend ha terminado con código', backend_proc.returncode)
                break
            if frontend_proc and frontend_proc.poll() is not None:
                print('\nEl proceso frontend ha terminado con código', frontend_proc.returncode)
                break
    except KeyboardInterrupt:
        print('\nInterrupción recibida. Deteniendo procesos...')
    finally:
        if backend_proc and backend_proc.poll() is None:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=3)
            except Exception:
                backend_proc.kill()
        if frontend_proc and frontend_proc.poll() is None:
            frontend_proc.terminate()
            try:
                frontend_proc.wait(timeout=3)
            except Exception:
                frontend_proc.kill()
        print('Procesos detenidos. Saliendo.')


if __name__ == '__main__':
    main()
