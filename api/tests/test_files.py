
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import File

class FileAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_list_files(self):
        response = self.client.get('/api/files/')
        self.assertEqual(response.status_code, 200)

    def test_create_file(self):
        data = {
            'name': 'image.png',
            'url': 'http://img.com/1',
            'file_type': 'image/png',
            'size': 5000,
            'file_id': 'abc',
            'original_name': 'image.png'
        }
        response = self.client.post('/api/files/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(File.objects.count(), 1)
