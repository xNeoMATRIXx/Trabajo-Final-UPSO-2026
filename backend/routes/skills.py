"""Habilidades de lenguajes y tecnologias, aisladas por usuario."""
from flask import Blueprint, g, jsonify
import mysql.connector

from models.database import Cursor
from . import auth_required, json_object
from .catalog import get_catalog


skills_bp = Blueprint("skills", __name__, url_prefix="/habilidades")
TIPOS = {"lenguaje", "tecnologia"}
NIVELES = {"basico", "intermedio", "avanzado"}


def skill_to_dict(row, catalog):
    element = (catalog.lenguaje(row["elemento_id"]) if row["tipo"] == "lenguaje"
               else catalog.tecnologia(row["elemento_id"]))
    return {
        "tipo": row["tipo"], "elemento_id": row["elemento_id"],
        "nombre": element["nombre"], "nivel": row["nivel"],
        "disponible": element.get("disponible", True),
    }


def valid_choice(value, options):
    return isinstance(value, str) and value in options


def parse_id(value):
    if type(value) is int and 0 < value <= 2147483647:
        return value
    return None


@skills_bp.get("")
@auth_required
def list_skills():
    catalog = get_catalog()
    with Cursor() as cursor:
        cursor.execute(
           "SELECT tipo, elemento_id, nivel FROM habilidades "
            "WHERE usuario_id = %s ORDER BY tipo, elemento_id",
            (g.user_id,),
        )
        rows = cursor.fetchall()
    return jsonify([skill_to_dict(row, catalog) for row in rows])


@skills_bp.post("")
@auth_required
def add_skill():
    data = json_object()
    tipo, element_id, level = data.get("tipo"), parse_id(data.get("elemento_id")), data.get("nivel")
    if not valid_choice(tipo, TIPOS) or element_id is None or not valid_choice(level, NIVELES):
        return jsonify({"error": "datos_invalidos"}), 400
    catalog = get_catalog()
    source = catalog.lenguajes_por_id if tipo == "lenguaje" else catalog.tecnologias_por_id
    if element_id not in source:
        return jsonify({"error": "elemento_no_existe_en_catalogo"}), 400
    try:
        with Cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO habilidades (usuario_id, tipo, elemento_id, nivel) VALUES (%s, %s, %s, %s)",
                (g.user_id, tipo, element_id, level),
            )
    except mysql.connector.IntegrityError as exc:
        if exc.errno == 1062:
            return jsonify({"error": "habilidad_ya_existe"}), 409
        raise
    return jsonify(skill_to_dict({"tipo": tipo, "elemento_id": element_id, "nivel": level}, catalog)), 201


@skills_bp.put("/<tipo>/<int:element_id>")
@auth_required
def update_skill(tipo, element_id):
    level = json_object().get("nivel")
    if not valid_choice(tipo, TIPOS) or parse_id(element_id) is None or not valid_choice(level, NIVELES):
        return jsonify({"error": "datos_invalidos"}), 400
    catalog = get_catalog()
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT tipo, elemento_id, nivel FROM habilidades "
            "WHERE usuario_id = %s AND tipo = %s AND elemento_id = %s FOR UPDATE",
            (g.user_id, tipo, element_id),
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "habilidad_no_encontrada"}), 404
        cursor.execute(
            "UPDATE habilidades SET nivel = %s WHERE usuario_id = %s AND tipo = %s AND elemento_id = %s",
            (level, g.user_id, tipo, element_id),
        )
    row["nivel"] = level
    return jsonify(skill_to_dict(row, catalog))


@skills_bp.delete("/<tipo>/<int:element_id>")
@auth_required
def delete_skill(tipo, element_id):
    if not valid_choice(tipo, TIPOS) or parse_id(element_id) is None:
        return jsonify({"error": "datos_invalidos"}), 400
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM habilidades WHERE usuario_id = %s AND tipo = %s AND elemento_id = %s",
            (g.user_id, tipo, element_id),
        )
        deleted = cursor.rowcount
    if not deleted:
        return jsonify({"error": "habilidad_no_encontrada"}), 404
    return jsonify({"mensaje": "habilidad_eliminada"})

