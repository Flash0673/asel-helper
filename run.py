import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "wine_detection"
FRONTEND = ROOT / "svoe-vino-scanner"
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(command, cwd, env):
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    env = os.environ.copy()
    try:
        node_version = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, check=True
        ).stdout.strip()
        if int(node_version.lstrip("v").split(".")[0]) < 22:
            sys.exit(f"Нужен Node.js 22 или 24 (сейчас {node_version}).")

        if not PYTHON.exists():
            print("Создаём Python-окружение…", flush=True)
            venv.create(VENV, with_pip=True)
        deps = VENV / ".deps-ready"
        if not deps.exists():
            print("Устанавливаем зависимости backend…", flush=True)
            run([str(PYTHON), "-m", "pip", "install", "-r", "requirements.txt"], BACKEND, env)
            deps.touch()

        node_marker = FRONTEND / "node_modules/.node-deps-ready"
        if not node_marker.exists() or node_marker.read_text() != node_version:
            print("Устанавливаем зависимости frontend…", flush=True)
            run(["npm.cmd" if os.name == "nt" else "npm", "ci", "--no-audit", "--no-fund"], FRONTEND, env)
            node_marker.write_text(node_version)

        print("Собираем frontend для работы с API…", flush=True)
        build_env = env.copy()
        build_env["NUXT_PUBLIC_USE_MOCK"] = "false"
        build_env["NUXT_PUBLIC_API_BASE"] = ""
        run(["npm.cmd" if os.name == "nt" else "npm", "run", "build"], FRONTEND, build_env)

        print("Своё вино: http://127.0.0.1:8000", flush=True)
        run([str(PYTHON), "-m", "uvicorn", "integration:app", "--host", "127.0.0.1", "--port", "8000"], ROOT, env)
    except FileNotFoundError as error:
        sys.exit(f"Не найдена программа {error.filename}. Установите Python 3.10+ и Node.js 22/24.")
    except subprocess.CalledProcessError as error:
        sys.exit(f"Шаг завершился с ошибкой (код {error.returncode}).")


if __name__ == "__main__":
    main()
