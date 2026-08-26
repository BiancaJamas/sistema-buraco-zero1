import unittest
from app import app  # Certifique-se de que seu arquivo principal se chama app.py

class BuracoZeroTestCase(unittest.TestCase):
    
    def setUp(self):
        # Configura o cliente de teste do Flask
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_pagina_principal(self):
        # Testa se a rota principal responde com sucesso (Status 200)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_pagina_denuncia(self):
        # Testa se a rota de denúncia carrega corretamente
        response = self.app.get('/denuncia')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()