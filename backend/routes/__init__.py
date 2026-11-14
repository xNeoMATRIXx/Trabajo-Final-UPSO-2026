"""Helpers compartidos por los blueprints de la API."""
from functools import wraps

import jwt
from flask import g, jsonify, request

from config import Config


def auth_required(view):
    """Valida el token Bearer y expone el ID del usuario mediante ``g.user_id``."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return jsonify({"error": "auth_required"}), 401

        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=[Config.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token_expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "token_invalid"}), 401

        user_id = payload.get("sub")
        if not isinstance(user_id, int):
            return jsonify({"error": "token_invalid"}), 401
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapped


def json_object():
    """Devuelve el cuerpo JSON si es un objeto; en otro caso un objeto vacío."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}
