import unittest
from app import app  # Import your Flask app

class TestCartCheckout(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_to_cart(self):
        response = self.app.post('/cart/add', json={
            'product_id': 1,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart_items', response.get_json())

    def test_checkout(self):
        response = self.app.post('/checkout', json={
            'payment_info': {
                'card_number': '1234-5678-9012-3456',
                'expiry': '12/24',
                'cvv': '123'
            }
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_id', response.get_json())

if __name__ == '__main__':
    unittest.main()
