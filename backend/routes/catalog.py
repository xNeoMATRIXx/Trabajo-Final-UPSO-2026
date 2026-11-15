"""Catalogos de solo lectura con fuente configurable."""
from flask import Blueprint, jsonify
from services.catalog_service import CatalogError, get_catalog

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.app_errorhandler(CatalogError)
def catalog_unavailable(error):
    return jsonify({"error": "catalogo_no_disponible", "mensaje": str(error)}), 503

@catalog_bp.get("/lenguajes")
def get_lenguajes():
    return jsonify(get_catalog().lenguajes)

@catalog_bp.get("/tecnologias")
def get_tecnologias():
    return jsonify(get_catalog().tecnologias)
