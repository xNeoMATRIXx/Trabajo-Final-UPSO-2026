"""Catálogos mock y HTTP; admite el header Grupo-Access-Key de la API oficial."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from flask import current_app, g

ROOT = Path(__file__).resolve().parents[1]


class CatalogError(RuntimeError):
    """Fuente inaccesible o incompatible con el contrato normalizado."""


def adaptar_lenguajes(payload):
    """Contrato verificado: lista de objetos con id y nombre."""
    return _normalizar(payload, tecnologia=False)


def adaptar_tecnologias(payload):
    """Contrato verificado: lista de objetos con id, nombre y categoria."""
    return _normalizar(payload, tecnologia=True)


def _normalizar(payload, tecnologia):
    if not isinstance(payload, list):
        raise CatalogError("La fuente no devuelve una lista compatible.")
    result, seen = [], set()
    for item in payload:
        if not isinstance(item, dict):
            raise CatalogError("Hay elementos incompatibles en el catalogo.")
        item_id, name = item.get("id"), item.get("nombre")
        if type(item_id) is not int or item_id <= 0 or item_id in seen:
            raise CatalogError("El catalogo contiene ids invalidos o duplicados.")
        if not isinstance(name, str) or not name.strip():
            raise CatalogError("El catalogo contiene nombres invalidos.")
        clean = {"id": item_id, "nombre": name.strip()}
        if tecnologia:
            category = item.get("categoria")
            if not isinstance(category, str) or not category.strip():
                raise CatalogError("La fuente no informa una categoria valida para la tecnologia.")
            clean["categoria"] = category.strip()
        seen.add(item_id)
        result.append(clean)
    return result


@dataclass(frozen=True)
class CatalogSnapshot:
    lenguajes: list
    tecnologias: list
    lenguajes_por_id: dict
    tecnologias_por_id: dict

    @classmethod
    def build(cls, languages, technologies):
        return cls(languages, technologies,
                   {x["id"]: x for x in languages},
                   {x["id"]: x for x in technologies})

    def lenguaje(self, item_id):
        return self.lenguajes_por_id.get(item_id, {
            "id": item_id, "nombre": f"Lenguaje no disponible (ID {item_id})",
            "disponible": False,
        })

    def tecnologia(self, item_id):
        return self.tecnologias_por_id.get(item_id, {
            "id": item_id, "nombre": f"Tecnologia no disponible (ID {item_id})",
            "disponible": False,
        })


class CatalogService:
    def __init__(self, mode="mock", base_url="", ttl=300, timeout=5,
                 languages_path="/lenguajes", technologies_path="/tecnologias",
                 token="", mock_file=None, auth_header="Authorization",
                 auth_prefix="Bearer"):
        if mode not in {"mock", "http"}:
            raise CatalogError("CATALOGO_MODO debe ser mock o http.")
        if mode == "http" and urlparse(base_url).scheme not in {"http", "https"}:
            raise CatalogError("Configura CATALOGO_API_URL con una URL HTTP o HTTPS.")
        if ttl < 0 or timeout <= 0:
            raise CatalogError("El TTL debe ser no negativo y el timeout positivo.")
        if not isinstance(auth_header, str) or not re.fullmatch(r"[A-Za-z0-9-]+", auth_header):
            raise CatalogError("CATALOGO_API_HEADER debe ser un nombre de header valido.")
        if not isinstance(token, str) or not isinstance(auth_prefix, str):
            raise CatalogError("La autenticacion del catalogo debe configurarse como texto.")
        if any(char in token + auth_prefix for char in "\r\n"):
            raise CatalogError("La configuracion de autenticacion del catalogo contiene saltos de linea.")
        self.mode, self.base_url = mode, base_url.rstrip("/")
        self.ttl, self.timeout, self.token = ttl, timeout, token
        self.languages_path, self.technologies_path = languages_path, technologies_path
        self.auth_header, self.auth_prefix = auth_header, auth_prefix.strip()
        self.mock_file = Path(mock_file) if mock_file else ROOT / "data/catalogo_prueba.json"
        self._snapshot, self._expires = None, 0
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls):
        try:
            return cls(
                mode=os.environ.get("CATALOGO_MODO", "mock").strip().lower(),
                base_url=os.environ.get("CATALOGO_API_URL", ""),
                ttl=float(os.environ.get("CATALOGO_CACHE_SEGUNDOS", "300")),
                timeout=float(os.environ.get("CATALOGO_TIMEOUT_SEGUNDOS", "5")),
                languages_path=os.environ.get("CATALOGO_LENGUAJES_PATH", "/lenguajes"),
                technologies_path=os.environ.get("CATALOGO_TECNOLOGIAS_PATH", "/tecnologias"),
                token=os.environ.get("CATALOGO_API_TOKEN", ""),
                auth_header=os.environ.get("CATALOGO_API_HEADER", "Authorization").strip(),
                auth_prefix=os.environ.get("CATALOGO_API_PREFIX", "Bearer"),
            )
        except ValueError as exc:
            raise CatalogError("La configuracion numerica del catalogo es invalida.") from exc

    def _http(self, path):
        headers = {"Accept": "application/json"}
        if self.token:
            value = self.token if not self.auth_prefix else self.auth_prefix + " " + self.token
            headers[self.auth_header] = value
        request = Request(self.base_url + "/" + path.lstrip("/"), headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read(2_000_001)
            if len(data) > 2_000_000:
                raise CatalogError("La respuesta del catalogo supera el limite previsto.")
            return json.loads(data.decode("utf-8-sig"))
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise CatalogError(
                    "La API del catalogo rechazo el acceso (HTTP %s). "
                    "Revisa CATALOGO_API_TOKEN, CATALOGO_API_HEADER y CATALOGO_API_PREFIX."
                    % exc.code
                ) from exc
            raise CatalogError("La API del catalogo respondio HTTP %s." % exc.code) from exc
        except (URLError, OSError, UnicodeError, ValueError) as exc:
            raise CatalogError("No se pudo obtener un catalogo JSON valido de la fuente HTTP.") from exc

    def read(self):
        with self._lock:
            if self._snapshot is not None and time.monotonic() < self._expires:
                return self._snapshot
            if self.mode == "mock":
                try:
                    payload = json.loads(self.mock_file.read_text(encoding="utf-8-sig"))
                    raw_languages, raw_technologies = payload["lenguajes"], payload["tecnologias"]
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    raise CatalogError("El catalogo de prueba no se puede leer.") from exc
            else:
                raw_languages = self._http(self.languages_path)
                raw_technologies = self._http(self.technologies_path)
            # Publicar solo cuando las DOS respuestas sean validas.
            snapshot = CatalogSnapshot.build(adaptar_lenguajes(raw_languages),
                                             adaptar_tecnologias(raw_technologies))
            self._snapshot, self._expires = snapshot, time.monotonic() + self.ttl
            return snapshot


def get_catalog():
    """Una instantanea coherente por peticion, con cache por aplicacion."""
    if "catalog_snapshot" not in g:
        service = current_app.extensions.get("catalog_service")
        if service is None:
            service = CatalogService.from_env()
            current_app.extensions["catalog_service"] = service
        g.catalog_snapshot = service.read()
    return g.catalog_snapshot
