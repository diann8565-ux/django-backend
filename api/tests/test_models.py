
from django.test import TestCase
from django.contrib.auth.models import User
from api.models import File, Category, StorageCredential

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='modeluser', password='password')
        self.category = Category.objects.create(user=self.user, name='Docs')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Docs')

    def test_file_creation(self):
        file = File.objects.create(
            user=self.user,
            name='test.txt',
            url='http://example.com/test.txt',
            file_type='text/plain',
            size=1024,
            file_id='123'
        )
        file.categories.add(self.category)
        self.assertEqual(file.categories.count(), 1)
        self.assertEqual(file.extension, 'txt') # Test auto extension
