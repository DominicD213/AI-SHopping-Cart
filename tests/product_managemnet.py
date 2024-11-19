import unittest
from app import app  # Import your Flask app

class TestProductManagement(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_product(self):
        response = self.app.post('/products', json={
            'name': 'Test Product',
            'price': 100.0,
            'embedding': [0.1, 0.2, 0.3]
        })
        self.assertEqual(response.status_code, 201)

    def test_get_product(self):
        response = self.app.get('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.get_json())

    def test_update_product(self):
        response = self.app.put('/products/1', json={
            'price': 90.0
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['price'], 90.0)

    def test_delete_product(self):
        response = self.app.delete('/products/1')
        self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main()
