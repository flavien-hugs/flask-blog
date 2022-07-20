import unittest
from core.models import User, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(password='password')
        self.assertTrue(user.password_hash is not None)

    def test_password_verification(self):
        user = User(password='password')
        self.assertFalse(user.verify_password('password'))

    def test_password_salts_are_random(self):
        user = User(password='password')
        user_two = User(password='Password')
        self.assertTrue(user.password != user_two.password)

    def test_user_role(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
