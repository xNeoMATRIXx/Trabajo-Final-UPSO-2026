"""Datos públicos del portfolio, sin información de autenticación."""
from flask import Blueprint, jsonify

from models.database import Cursor
from . import json_object
from .projects import _find_projects
from .catalog import get_catalog
from .skills import skill_to_dict


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
            "SELECT tipo, elemento_id, nivel FROM habilidades WHERE usuario_id = %s "
            "ORDER BY tipo, elemento_id",
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
        "habilidades": [skill_to_dict(item, get_catalog()) for item in skills],
        "proyectos": projects,
    })
