import unittest
from flask import Flask
from app import app  # Import your Flask app
from models import User  # Your User model

class TestUserManagement(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_success(self):
        response = self.app.post('/login', json={
            'username': 'test_user',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_login_failure(self):
        response = self.app.post('/login', json={
            'username': 'wrong_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)

    def test_access_control(self):
        response = self.app.get('/admin/dashboard', headers={
            'Authorization': 'Bearer invalid_token'
        })
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
