from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    def test_user_can_be_created_with_provider_role(self):
        user = User.objects.create_user(
            username='provider1',
            email='provider@example.com',
            password='secret123',
            role='PROVIDER',
        )

        self.assertEqual(user.role, 'PROVIDER')
        self.assertTrue(user.check_password('secret123'))
