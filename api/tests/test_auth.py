
from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Profile

class AuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_profile_creation(self):
        """Test that a profile is automatically created when a user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)

    def test_user_login(self):
        login = self.client.login(username='testuser', password='password123')
        self.assertTrue(login)
