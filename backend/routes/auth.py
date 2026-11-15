"""Registro, inicio de sesión y administración de la cuenta."""
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import mysql.connector
from flask import Blueprint, g, jsonify

from config import Config
from models.database import Cursor
from . import auth_required, json_object


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")


def _public_user(row):
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "nombre": row["nombre"],
        "bio": row["bio"],
    }


def _create_token(user_id):
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(hours=Config.JWT_EXP_HOURS),
        },
        Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )


@auth_bp.post("/register")
def register():
    data = json_object()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    nombre = data.get("nombre")
    bio = data.get("bio")

    if not isinstance(email, str) or not EMAIL_RE.fullmatch(email.strip()):
        return jsonify({"error": "email_invalido"}), 400
    email = email.strip().lower()
    if not isinstance(username, str) or not USERNAME_RE.fullmatch(username):
        return jsonify({"error": "username_invalido"}), 400
    if not isinstance(password, str) or len(password) < 6:
        return jsonify({"error": "password_invalido"}), 400
    if nombre is not None and not isinstance(nombre, str):
        return jsonify({"error": "datos_invalidos"}), 400
    if bio is not None and not isinstance(bio, str):
        return jsonify({"error": "datos_invalidos"}), 400

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with Cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO usuarios (email, username, password_hash, nombre, bio) "
                "VALUES (%s, %s, %s, %s, %s)",
                (email, username, password_hash, nombre, bio),
            )
            user = {
                "id": cursor.lastrowid,
                "email": email,
                "username": username,
                "nombre": nombre,
                "bio": bio,
            }
    except mysql.connector.IntegrityError:
        with Cursor() as cursor:
            cursor.execute(
                "SELECT email, username FROM usuarios WHERE email = %s OR username = %s",
                (email, username),
            )
            existing = cursor.fetchone()
        if existing and existing["email"] == email:
            return jsonify({"error": "email_ya_registrado"}), 409
        if existing and existing["username"] == username:
            return jsonify({"error": "username_ya_usado"}), 409
        raise

    return jsonify({"token": _create_token(user["id"]), "user": user}), 201


@auth_bp.post("/login")
def login():
    data = json_object()
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "credenciales_invalidas"}), 401

    with Cursor() as cursor:
        cursor.execute(
            "SELECT id, email, username, password_hash, nombre, bio "
            "FROM usuarios WHERE email = %s",
            (email.strip().lower(),),
        )
        row = cursor.fetchone()

    if row is None or not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return jsonify({"error": "credenciales_invalidas"}), 401
    user = _public_user(row)
    return jsonify({"token": _create_token(user["id"]), "user": user})


@auth_bp.get("/me")
@auth_required
def me():
    with Cursor() as cursor:
        cursor.execute(
            "SELECT id, email, username, nombre, bio FROM usuarios WHERE id = %s",
            (g.user_id,),
        )
        row = cursor.fetchone()
    if row is None:
        return jsonify({"error": "usuario_no_encontrado"}), 404
    return jsonify({"user": _public_user(row)})

@auth_bp.put("/me")
@auth_required
def update_me():
    data = json_object()

    allowed = {"email", "username", "nombre", "bio"}
    if set(data) - allowed:
        return jsonify({"error": "campos_no_permitidos"}), 400

    email = data.get("email")
    username = data.get("username")
    nombre = data.get("nombre")
    bio = data.get("bio")

    if not isinstance(email, str):
        return jsonify({"error": "email_invalido"}), 400

    email = email.strip().lower()
    if len(email) > 190 or not EMAIL_RE.fullmatch(email):
        return jsonify({"error": "email_invalido"}), 400

    if not isinstance(username, str):
        return jsonify({"error": "username_invalido"}), 400

    username = username.strip()
    if not USERNAME_RE.fullmatch(username):
        return jsonify({"error": "username_invalido"}), 400

    if nombre is not None and (
        not isinstance(nombre, str) or len(nombre) > 120
    ):
        return jsonify({"error": "nombre_invalido"}), 400

    if bio is not None and (
        not isinstance(bio, str) or len(bio) > 5000
    ):
        return jsonify({"error": "bio_invalida"}), 400

    nombre = (nombre.strip() or None) if nombre is not None else None
    bio = (bio.strip() or None) if bio is not None else None

    try:
        with Cursor(commit=True) as cursor:
            # La identidad proviene exclusivamente del token.
            cursor.execute(
                "SELECT id FROM usuarios WHERE id = %s FOR UPDATE",
                (g.user_id,),
            )

            if cursor.fetchone() is None:
                return jsonify({"error": "usuario_no_encontrado"}), 404

            # Permitir conservar el email propio, pero no usar el de otro.
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s AND id <> %s",
                (email, g.user_id),
            )

            if cursor.fetchone() is not None:
                return jsonify({"error": "email_ya_registrado"}), 409

            cursor.execute(
                "SELECT id FROM usuarios WHERE username = %s AND id <> %s",
                (username, g.user_id),
            )

            if cursor.fetchone() is not None:
                return jsonify({"error": "username_ya_usado"}), 409

            cursor.execute(
                "UPDATE usuarios "
                "SET email = %s, username = %s, nombre = %s, bio = %s "
                "WHERE id = %s",
                (email, username, nombre, bio, g.user_id),
            )

            cursor.execute(
                "SELECT id, email, username, nombre, bio "
                "FROM usuarios WHERE id = %s",
                (g.user_id,),
            )
            row = cursor.fetchone()

    except mysql.connector.IntegrityError as exc:
        # También cubre duplicados producidos por peticiones simultáneas.
        if exc.errno == 1062:
            return jsonify({
                "error": "email_o_username_ya_utilizado"
            }), 409
        raise

    return jsonify({"user": _public_user(row)})


@auth_bp.delete("/me")
@auth_required
def delete_me():
    with Cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (g.user_id,))
        deleted = cursor.rowcount
    if not deleted:
        return jsonify({"error": "usuario_no_encontrado"}), 404
    return jsonify({"mensaje": "cuenta_eliminada"})
