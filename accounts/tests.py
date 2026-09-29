from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('api-register')
        self.login_url = reverse('api-login')
        self.valid_payload = {
            'name': 'Michan',
            'email': 'michan@gmail.com',
            'password': 'michan123'
        }

    def test_api_registration_success(self):
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'michan@gmail.com')
        self.assertEqual(response.data['user']['name'], 'Michan')
        self.assertNotIn('password', response.data['user'])
        self.assertTrue(User.objects.filter(email='michan@gmail.com').exists())

    def test_api_registration_duplicate_email(self):
        User.objects.create_user(
            email='michan@gmail.com',
            name='Existing User',
            password='password123'
        )
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_api_login_success(self):
        User.objects.create_user(
            email='michan@gmail.com',
            name='Michan',
            password='michan123'
        )
        login_data = {
            'email': 'michan@gmail.com',
            'password': 'michan123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_api_login_invalid_credentials(self):
        User.objects.create_user(
            email='michan@gmail.com',
            name='Michan',
            password='michan123'
        )
        invalid_login = {
            'email': 'michan@gmail.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BrowserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_post_success(self):
        data = {
            'name': 'Michan',
            'email': 'michan@gmail.com',
            'password': 'michan123',
            'confirm_password': 'michan123'
        }
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(email='michan@gmail.com').exists())

    def test_register_post_password_mismatch(self):
        data = {
            'name': 'Michan',
            'email': 'michan@gmail.com',
            'password': 'michan123',
            'confirm_password': 'mismatchpassword'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='michan@gmail.com').exists())

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_post_success(self):
        User.objects.create_user(
            email='michan@gmail.com',
            name='Michan',
            password='michan123'
        )
        data = {
            'email': 'michan@gmail.com',
            'password': 'michan123'
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, '/patients/', fetch_redirect_response=False)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_post_invalid(self):
        data = {
            'email': 'nonexistent@gmail.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout(self):
        user = User.objects.create_user(
            email='michan@gmail.com',
            name='Michan',
            password='michan123'
        )
        self.client.force_login(user)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)
