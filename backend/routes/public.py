"""Datos públicos del portfolio, sin información de autenticación."""
from flask import Blueprint, jsonify

from models.database import Cursor
from . import json_object
from .projects import _find_projects
from .catalog import TECNOLOGIAS_POR_ID


public_bp = Blueprint("public", __name__)


@public_bp.get("/u/<username>")
def public_profile(username):
    with Cursor() as cursor:
        cursor.execute(
            "SELECT id, username, nombre, bio FROM usuarios WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "usuario_no_encontrado"}), 404

        cursor.execute(
            "SELECT tecnologia_id, nivel FROM habilidades WHERE usuario_id = %s "
            "ORDER BY tecnologia_id",
            (user["id"],),
        )
        skills = cursor.fetchall()
        projects = _find_projects(cursor, user["id"])

    return jsonify({
        "perfil": {
            "username": user["username"],
            "nombre": user["nombre"],
            "bio": user["bio"],
        },
        "habilidades": [
            {
                "tecnologia_id": item["tecnologia_id"],
                "tecnologia": TECNOLOGIAS_POR_ID[item["tecnologia_id"]]["nombre"],
                "nivel": item["nivel"],
            }
            for item in skills
        ],
        "proyectos": projects,
    })
