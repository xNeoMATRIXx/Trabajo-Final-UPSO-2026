"""CRUD de proyectos y serialización de sus relaciones."""
from datetime import date, datetime

from flask import Blueprint, g, jsonify

from models.database import Cursor
from . import auth_required, json_object
from .catalog import get_catalog


projects_bp = Blueprint("projects", __name__, url_prefix="/proyectos")
ETAPAS = {"formulacion", "modelado", "implementacion", "testing", "produccion", "mantenimiento"}
TIPOS_LINK = {"repositorio", "demo", "documentacion", "video", "otro"}


def _iso(value):
    return value.isoformat() if isinstance(value, (date, datetime)) else value


def _id_list(data, key, catalog):
    values = data.get(key, [])
    if not isinstance(values, list):
        return None
    result = []
    for value in values:
        if isinstance(value, bool):
            return None
        try:
            item_id = int(value)
        except (TypeError, ValueError):
            return None
        if item_id not in catalog:
            return None
        if item_id not in result:
            result.append(item_id)
    return result


def _validated_project(data):
    if not isinstance(data.get("nombre"), str) or not data["nombre"].strip():
        return None, "nombre_invalido"
    if len(data["nombre"].strip()) > 160:
        return None, "nombre_invalido"
    if data.get("descripcion") is not None and not isinstance(data.get("descripcion"), str):
        return None, "descripcion_invalida"
    if data.get("etapa") not in ETAPAS:
        return None, "etapa_invalida"

    catalog = get_catalog()
    languages = _id_list(data, "lenguajes", catalog.lenguajes_por_id)
    technologies = _id_list(data, "tecnologias", catalog.tecnologias_por_id)
    links = data.get("links", [])

    # Rechazar listas incorrectas o IDs ajenos al catálogo.
    if languages is None or technologies is None or not isinstance(links, list):
        return None, "relaciones_invalidas"

    # Exigir al menos un elemento de cada catálogo.
    if not languages:
        return None, "lenguajes_requeridos"

    if not technologies:
        return None, "tecnologias_requeridas"

    clean_links = []
    for link in links:
        if not isinstance(link, dict):
            return None, "links_invalidos"
        kind, url = link.get("tipo"), link.get("url")
        if kind not in TIPOS_LINK or not isinstance(url, str) or not url.strip() or len(url.strip()) > 500:
            return None, "links_invalidos"
        clean_links.append({"tipo": kind, "url": url.strip()})

    project = {
        "nombre": data["nombre"].strip(),
        "descripcion": data.get("descripcion"),
        "etapa": data["etapa"],
        "fecha_deadline": data.get("fecha_deadline") or None,
        "fecha_finalizacion": data.get("fecha_finalizacion") or None,
        "lenguajes": languages,
        "tecnologias": technologies,
        "links": clean_links,
    }
    for key in ("fecha_deadline", "fecha_finalizacion"):
        value = project[key]
        if value is not None:
            try:
                date.fromisoformat(value)
            except (TypeError, ValueError):
                return None, "fecha_invalida"
    return project, None


def _project_ids(cursor, project_id, table, column):
    cursor.execute(
        f"SELECT {column} FROM {table} WHERE proyecto_id = %s ORDER BY {column}",
        (project_id,),
    )
    return [row[column] for row in cursor.fetchall()]


def _load_project(cursor, row):
    catalog = get_catalog()
    project_id = row["id"]
    language_ids = _project_ids(cursor, project_id, "proyecto_lenguaje", "lenguaje_id")
    technology_ids = _project_ids(cursor, project_id, "proyecto_tecnologia", "tecnologia_id")
    cursor.execute(
        "SELECT tipo, url FROM proyecto_links WHERE proyecto_id = %s ORDER BY id",
        (project_id,),
    )
    links = cursor.fetchall()
    return {
        "id": project_id,
        "nombre": row["nombre"],
        "descripcion": row["descripcion"],
        "etapa": row["etapa"],
        "fecha_creacion": _iso(row["fecha_creacion"]),
        "fecha_actualizacion": _iso(row["fecha_actualizacion"]),
        "fecha_finalizacion": _iso(row["fecha_finalizacion"]),
        "fecha_deadline": _iso(row["fecha_deadline"]),
        "lenguajes": [catalog.lenguaje(item_id) for item_id in language_ids],
        "tecnologias": [catalog.tecnologia(item_id) for item_id in technology_ids],
        "links": links,
    }


def _find_projects(cursor, user_id):
    cursor.execute(
        "SELECT id, nombre, descripcion, etapa, fecha_creacion, fecha_actualizacion, "
        "fecha_finalizacion, fecha_deadline FROM proyectos "
        "WHERE usuario_id = %s ORDER BY fecha_creacion DESC, id DESC",
        (user_id,),
    )
    return [_load_project(cursor, row) for row in cursor.fetchall()]


def _write_relations(cursor, project_id, project):
    cursor.execute("DELETE FROM proyecto_lenguaje WHERE proyecto_id = %s", (project_id,))
    cursor.execute("DELETE FROM proyecto_tecnologia WHERE proyecto_id = %s", (project_id,))
    cursor.execute("DELETE FROM proyecto_links WHERE proyecto_id = %s", (project_id,))
    if project["lenguajes"]:
        cursor.executemany(
            "INSERT INTO proyecto_lenguaje (proyecto_id, lenguaje_id) VALUES (%s, %s)",
            [(project_id, item_id) for item_id in project["lenguajes"]],
        )
    if project["tecnologias"]:
        cursor.executemany(
            "INSERT INTO proyecto_tecnologia (proyecto_id, tecnologia_id) VALUES (%s, %s)",
            [(project_id, item_id) for item_id in project["tecnologias"]],
        )
    if project["links"]:
        cursor.executemany(
            "INSERT INTO proyecto_links (proyecto_id, tipo, url) VALUES (%s, %s, %s)",
            [(project_id, item["tipo"], item["url"]) for item in project["links"]],
        )


@projects_bp.get("")
@auth_required
def list_projects():
    with Cursor() as cursor:
        projects = _find_projects(cursor, g.user_id)
    return jsonify(projects)


@projects_bp.post("")
@auth_required
def create_project():
    project, error = _validated_project(json_object())
    if error:
        return jsonify({"error": error}), 400
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO proyectos (usuario_id, nombre, descripcion, etapa, fecha_deadline, fecha_finalizacion) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                g.user_id, project["nombre"], project["descripcion"], project["etapa"],
                project["fecha_deadline"], project["fecha_finalizacion"],
            ),
        )
        project_id = cursor.lastrowid
        _write_relations(cursor, project_id, project)
    with Cursor() as cursor:
        cursor.execute(
            "SELECT id, nombre, descripcion, etapa, fecha_creacion, fecha_actualizacion, "
            "fecha_finalizacion, fecha_deadline FROM proyectos WHERE id = %s AND usuario_id = %s",
            (project_id, g.user_id),
        )
        result = _load_project(cursor, cursor.fetchone())
    return jsonify(result), 201


@projects_bp.put("/<int:project_id>")
@auth_required
def update_project(project_id):
    project, error = _validated_project(json_object())
    if error:
        return jsonify({"error": error}), 400
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE proyectos SET nombre = %s, descripcion = %s, etapa = %s, "
            "fecha_deadline = %s, fecha_finalizacion = %s, "
            "fecha_actualizacion = CURRENT_TIMESTAMP "
            "WHERE id = %s AND usuario_id = %s",
            (
                project["nombre"], project["descripcion"], project["etapa"],
                project["fecha_deadline"], project["fecha_finalizacion"],
                project_id, g.user_id,
            ),
        )
        cursor.execute("SELECT id FROM proyectos WHERE id = %s AND usuario_id = %s", (project_id, g.user_id))
        exists = cursor.fetchone()
        if not exists:
            return jsonify({"error": "proyecto_no_encontrado"}), 404
        _write_relations(cursor, project_id, project)

    with Cursor() as cursor:
        cursor.execute(
            "SELECT id, nombre, descripcion, etapa, fecha_creacion, fecha_actualizacion, "
            "fecha_finalizacion, fecha_deadline FROM proyectos WHERE id = %s AND usuario_id = %s",
            (project_id, g.user_id),
        )
        result = _load_project(cursor, cursor.fetchone())
    return jsonify(result)


@projects_bp.delete("/<int:project_id>")
@auth_required
def delete_project(project_id):
    with Cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM proyectos WHERE id = %s AND usuario_id = %s", (project_id, g.user_id))
        deleted = cursor.rowcount
    if not deleted:
        return jsonify({"error": "proyecto_no_encontrado"}), 404
    return jsonify({"mensaje": "proyecto_eliminado"})
