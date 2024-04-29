import unittest
from app import app, db
from app.models import User

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_intro_route(self):
        response = self.app.get('/intro')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Intro', response.data)

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_with_valid_credentials(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        response = self.app.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_login_with_invalid_credentials(self):
        response = self.app.post('/login', data={'username': 'invaliduser', 'password': 'invalidpassword'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_with_valid_credentials(self):
        response = self.app.post('/register', data={'username': 'newuser', 'email': 'newuser@example.com', 'password': 'newpassword'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_register_with_existing_username(self):
        user = User(username='existinguser', email='existing@example.com')
        user.set_password('existingpassword')
        db.session.add(user)
        db.session.commit()

        response = self.app.post('/register', data={'username': 'existinguser', 'email': 'newuser@example.com', 'password': 'newpassword'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

if __name__ == '__main__':
    unittest.main()
