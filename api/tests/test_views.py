
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class ViewTestCase(APITestCase):
    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
