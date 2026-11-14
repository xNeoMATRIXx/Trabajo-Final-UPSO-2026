"""Catálogos estáticos de lenguajes y tecnologías."""
from flask import Blueprint, jsonify


catalog_bp = Blueprint("catalog", __name__)

LENGUAJES = [
    {"id": 1, "nombre": "Python"},
    {"id": 2, "nombre": "JavaScript"},
    {"id": 3, "nombre": "TypeScript"},
    {"id": 4, "nombre": "Java"},
    {"id": 5, "nombre": "C#"},
    {"id": 6, "nombre": "C++"},
    {"id": 7, "nombre": "PHP"},
    {"id": 8, "nombre": "Go"},
    {"id": 9, "nombre": "Ruby"},
    {"id": 10, "nombre": "Rust"},
    {"id": 11, "nombre": "SQL"},
    {"id": 12, "nombre": "HTML"},
    {"id": 13, "nombre": "CSS"},
]

TECNOLOGIAS = [
    {"id": 1, "nombre": "React"},
    {"id": 2, "nombre": "Vue"},
    {"id": 3, "nombre": "Angular"},
    {"id": 4, "nombre": "Node.js"},
    {"id": 5, "nombre": "Express"},
    {"id": 6, "nombre": "Flask"},
    {"id": 7, "nombre": "Django"},
    {"id": 8, "nombre": "Laravel"},
    {"id": 9, "nombre": ".NET"},
    {"id": 10, "nombre": "MySQL"},
    {"id": 11, "nombre": "PostgreSQL"},
    {"id": 12, "nombre": "MongoDB"},
    {"id": 13, "nombre": "Docker"},
    {"id": 14, "nombre": "Git"},
    {"id": 15, "nombre": "AWS"},
]

LENGUAJES_POR_ID = {item["id"]: item for item in LENGUAJES}
TECNOLOGIAS_POR_ID = {item["id"]: item for item in TECNOLOGIAS}


@catalog_bp.get("/lenguajes")
def get_lenguajes():
    return jsonify(LENGUAJES)


@catalog_bp.get("/tecnologias")
def get_tecnologias():
    return jsonify(TECNOLOGIAS)
