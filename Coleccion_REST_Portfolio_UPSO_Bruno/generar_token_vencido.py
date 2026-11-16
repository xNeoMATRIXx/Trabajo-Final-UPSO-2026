"""Ejecutar desde backend con su .venv. Configura solo un token YA vencido."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sys

backend = Path.cwd()
if not (backend / "config.py").is_file():
    raise SystemExit("Abrí una terminal en la carpeta backend antes de ejecutar este archivo.")
sys.path.insert(0, str(backend))
try:
    import jwt
    from config import Config
except ImportError as exc:
    raise SystemExit("Usá el Python de la .venv del backend, con sus dependencias instaladas.") from exc

now = datetime.now(timezone.utc)
token = jwt.encode(
    {"sub": 1, "iat": now - timedelta(hours=1), "exp": now - timedelta(minutes=2)},
    Config.JWT_SECRET,
    algorithm=Config.JWT_ALGORITHM,
)
environment = Path(__file__).resolve().parent / "Portfolio_UPSO_Bruno/environments/Local.yml"
source = environment.read_text(encoding="utf-8")
updated, count = re.subn(
    r"(- name: expired_token\s*\n\s*value:)[^\n]*",
    lambda match: match.group(1) + " '" + token + "'",
    source,
)
if count != 1:
    raise SystemExit("No se encontró expired_token en el entorno Local de la colección.")
environment.write_text(updated, encoding="utf-8")
print("Token vencido configurado en el entorno Local. No se mostró ni modificó JWT_SECRET.")
print("Abrí o recargá el entorno Local en Bruno y ejecutá la colección desde el inicio.")
