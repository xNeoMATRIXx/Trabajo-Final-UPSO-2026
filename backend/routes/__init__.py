"""Helpers compartidos por los blueprints de la API."""
from functools import wraps

import jwt
from flask import g, jsonify, request
from werkzeug.exceptions import BadRequest

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
        if not valid_id(user_id):
            return jsonify({"error": "token_invalid"}), 401
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapped


def json_object():
    if not request.is_json:
        raise BadRequest(
            "Enviá el cuerpo con Content-Type: application/json."
        )

    try:
        data = request.get_json()
    except BadRequest as exc:
        raise BadRequest(
            "El cuerpo no contiene JSON válido."
        ) from exc

    if not isinstance(data, dict):
        raise BadRequest(
            "El JSON debe ser un objeto, no una lista u otro valor."
        )

    return data

def valid_id(value):
    return type(value) is int and 1 <= value <= 2147483647


def valid_text(value, max_chars=None, max_bytes=None):
    if not isinstance(value, str):
        return False

    if max_chars is not None and len(value) > max_chars:
        return False

    try:
        encoded = value.encode("utf-8")
    except UnicodeError:
        return False

    return max_bytes is None or len(encoded) <= max_bytes
