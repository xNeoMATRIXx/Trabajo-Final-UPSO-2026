"""Pruebas sin MySQL: python -m unittest discover -s tests -p test_catalogo.py -v"""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from app import create_app
from mock_catalogo import Handler
from routes.auth import _create_token
from routes.projects import _validated_project
from services.catalog_service import CatalogError, CatalogService


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


class CatalogTests(unittest.TestCase):
    def test_mock_includes_categories(self):
        catalog = CatalogService().read()
        self.assertTrue(catalog.lenguajes)
        self.assertTrue(all(x['categoria'] for x in catalog.tecnologias))

    def test_http_reads_local_mock(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            service = CatalogService(mode='http', base_url=f'http://127.0.0.1:{server.server_port}')
            self.assertEqual(service.read().lenguajes, CatalogService().read().lenguajes)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_valid_cache_survives_source_outage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'catalogo.json'
            path.write_bytes(CatalogService().mock_file.read_bytes())
            service = CatalogService(mock_file=path, ttl=60)
            expected = service.read()
            path.unlink()
            self.assertEqual(service.read().lenguajes, expected.lenguajes)

    def test_expired_cache_does_not_silently_fall_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'catalogo.json'
            path.write_bytes(CatalogService().mock_file.read_bytes())
            service = CatalogService(mock_file=path, ttl=0)
            service.read()
            path.unlink()
            with self.assertRaises(CatalogError):
                service.read()

    def test_duplicate_ids_are_rejected(self):
        data = {'lenguajes':[{'id':1,'nombre':'Python'},{'id':1,'nombre':'Otro'}], 'tecnologias':[]}
        self.assert_invalid_file(data)

    def test_missing_category_is_rejected(self):
        self.assert_invalid_file({'lenguajes':[], 'tecnologias':[{'id':1,'nombre':'React'}]})

    def assert_invalid_file(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'catalogo.json'
            path.write_text(json.dumps(data))
            with self.assertRaises(CatalogError):
                CatalogService(mock_file=path).read()

    def test_removed_reference_can_still_be_displayed(self):
        item = CatalogService().read().tecnologia(999999)
        self.assertEqual(item['id'], 999999)
        self.assertFalse(item['disponible'])


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.extensions['catalog_service'] = CatalogService(ttl=0)
        self.client = self.app.test_client()
        self.headers = {'Authorization':'Bearer '+_create_token(1)}

    def test_get_catalogs(self):
        for path in ['/lenguajes','/tecnologias']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.get_json(), list)

    def test_catalogs_reject_writes(self):
        for path in ['/lenguajes','/tecnologias']:
            for method in ['POST','PUT','PATCH','DELETE']:
                response = self.client.open(path, method=method, json={'nombre':'Inventado'})
                self.assertEqual(response.status_code, 405)

    def test_unknown_skill_id_is_rejected_before_database(self):
        with patch('routes.skills.Cursor', side_effect=AssertionError('No debe consultar MySQL')):
            response = self.client.post('/habilidades', json={'tecnologia_id':999999,'nivel':'basico'}, headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_unknown_project_reference_is_rejected_before_database(self):
        with patch('routes.projects.Cursor', side_effect=AssertionError('No debe consultar MySQL')):
            response = self.client.post('/proyectos', json={
                'nombre':'Prueba','etapa':'testing','lenguajes':[999999],'tecnologias':[1]}, headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_known_project_references_pass_validation(self):
        with self.app.test_request_context():
            result, error = _validated_project({'nombre':'Prueba','etapa':'testing','lenguajes':[1,2],'tecnologias':[1,2]})
            self.assertIsNone(error)
            self.assertEqual(result['lenguajes'], [1,2])

    def test_outage_returns_503_json(self):
        service = CatalogService(mode='http', base_url='http://127.0.0.1:5001')
        self.app.extensions['catalog_service'] = service
        with patch.object(service, '_http', side_effect=CatalogError('Fuente no disponible')):
            response = self.client.get('/tecnologias')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()['error'], 'catalogo_no_disponible')

    def test_http_mode_does_not_use_mock_when_source_fails(self):
        service = CatalogService(mode='http', base_url='http://127.0.0.1:5001')
        with patch.object(service, '_http', side_effect=CatalogError('Error de fuente')):
            with self.assertRaises(CatalogError):
                service.read()

    def test_authentication_still_required_for_skills(self):
        response = self.client.post('/habilidades', json={'tecnologia_id':1,'nivel':'basico'})
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
