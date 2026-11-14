"""Operaciones autenticadas sobre las habilidades del usuario."""
from flask import Blueprint, g, jsonify
import mysql.connector

from models.database import Cursor
from . import auth_required, json_object
from .catalog import TECNOLOGIAS_POR_ID


skills_bp = Blueprint("skills", __name__, url_prefix="/habilidades")
NIVELES = {"basico", "intermedio", "avanzado"}


def _parse_technology_id(value):
    if isinstance(value, bool):
        return None
    try:
        technology_id = int(value)
    except (TypeError, ValueError):
        return None
    return technology_id if technology_id in TECNOLOGIAS_POR_ID else None


@skills_bp.get("")
@auth_required
def list_skills():
    with Cursor() as cursor:
        cursor.execute(
            "SELECT tecnologia_id, nivel FROM habilidades WHERE usuario_id = %s "
            "ORDER BY tecnologia_id",
            (g.user_id,),
        )
        rows = cursor.fetchall()
    return jsonify([
        {
            "tecnologia_id": row["tecnologia_id"],
            "tecnologia": TECNOLOGIAS_POR_ID[row["tecnologia_id"]]["nombre"],
            "nivel": row["nivel"],
        }
        for row in rows
    ])


@skills_bp.post("")
@auth_required
def add_skill():
    data = json_object()
    technology_id = _parse_technology_id(data.get("tecnologia_id"))
    level = data.get("nivel")
    if technology_id is None or level not in NIVELES:
        return jsonify({"error": "datos_invalidos"}), 400

    try:
        with Cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO habilidades (usuario_id, tecnologia_id, nivel) VALUES (%s, %s, %s)",
                (g.user_id, technology_id, level),
            )
    except mysql.connector.IntegrityError:
        return jsonify({"error": "habilidad_ya_existe"}), 409
    return jsonify({
        "tecnologia_id": technology_id,
        "tecnologia": TECNOLOGIAS_POR_ID[technology_id]["nombre"],
        "nivel": level,
    }), 201


@skills_bp.put("/<int:technology_id>")
@auth_required
def update_skill(technology_id):
    data = json_object()
    level = data.get("nivel")
    if technology_id not in TECNOLOGIAS_POR_ID or level not in NIVELES:
        return jsonify({"error": "datos_invalidos"}), 400
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE habilidades SET nivel = %s WHERE usuario_id = %s AND tecnologia_id = %s",
            (level, g.user_id, technology_id),
        )
        updated = cursor.rowcount
    if not updated:
        return jsonify({"error": "habilidad_no_encontrada"}), 404
    return jsonify({
        "tecnologia_id": technology_id,
        "tecnologia": TECNOLOGIAS_POR_ID[technology_id]["nombre"],
        "nivel": level,
    })


@skills_bp.delete("/<int:technology_id>")
@auth_required
def delete_skill(technology_id):
    with Cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM habilidades WHERE usuario_id = %s AND tecnologia_id = %s",
            (g.user_id, technology_id),
        )
        deleted = cursor.rowcount
    if not deleted:
        return jsonify({"error": "habilidad_no_encontrada"}), 404
    return jsonify({"mensaje": "habilidad_eliminada"})
