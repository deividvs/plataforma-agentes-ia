"""Gerencia API, worker e agendador locais sem carregar .env pelo shell."""
from pathlib import Path
import argparse
import os
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values

RUN = ROOT / 'var/run'
LOG = ROOT / 'var/logs'
PYTHON = ROOT / '.venv/bin/python'
SERVICES = {
    'api': [str(PYTHON), '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8002'],
    'worker': [str(PYTHON), '-m', 'celery', '-A', 'backend.worker.celery_app:app', 'worker', '--loglevel=INFO', '--pool=solo', '--hostname=cdc-agentes@%h'],
    'beat': [str(PYTHON), '-m', 'celery', '-A', 'backend.worker.celery_app:app', 'beat', '--loglevel=INFO', '--schedule', str(RUN / 'celerybeat-schedule')],
}

def running(name):
    path = RUN / (name + '.pid')
    if not path.exists():
        return None
    pid = int(path.read_text())
    try:
        os.kill(pid, 0)
        command = subprocess.check_output(['ps', '-p', str(pid), '-o', 'command='], text=True)
        if str(PYTHON) not in command:
            return None
        return pid
    except PermissionError:
        # A sandbox may deny process inspection even when the service is alive.
        return pid
    except (ProcessLookupError, subprocess.CalledProcessError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start', 'stop', 'status', 'migrate', 'check-db'])
    args = parser.parse_args()
    env = os.environ.copy()
    env.update({k: v for k, v in dotenv_values(ROOT / 'backend/.env').items() if v is not None})
    env['PYTHONPATH'] = str(ROOT)
    env['PGOPTIONS'] = '-c search_path=cdc_agentes'
    env['PGSSLMODE'] = 'require'
    RUN.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    if args.action in ['start', 'migrate', 'check-db']:
        from sqlalchemy.engine import make_url
        try:
            url = make_url(env['DATABASE_URL'])
            if not url.host or not url.host.endswith('.supabase.com') and not url.host.endswith('.supabase.co'):
                raise ValueError('Configure a URI PostgreSQL do CENTRAL em backend/.env.')
            env['DATABASE_URL'] = url.set(drivername='postgresql+psycopg2').render_as_string(hide_password=False)
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))
    if args.action in ['migrate', 'check-db']:
        operation = ['upgrade', 'head'] if args.action == 'migrate' else ['check']
        return subprocess.call([str(PYTHON), '-m', 'alembic', *operation], cwd=ROOT / 'backend', env=env)
    for name, command in SERVICES.items():
        pid = running(name)
        if args.action == 'status':
            print(f'{name}: ' + (f'ativo (PID {pid})' if pid else 'parado'))
        elif args.action == 'stop' and pid:
            os.killpg(pid, signal.SIGTERM)
            (RUN / (name + '.pid')).unlink(missing_ok=True)
            print(f'{name}: encerramento solicitado')
        elif args.action == 'start' and not pid:
            with (LOG / (name + '.log')).open('a') as output:
                process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            (RUN / (name + '.pid')).write_text(str(process.pid))
            print(f'{name}: iniciado (PID {process.pid}); consulte var/logs/{name}.log')
        else:
            print(f'{name}: sem alteração')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
