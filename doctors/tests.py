from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Doctor

User = get_user_model()


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email='doctor_user_a@example.com',
            name='User A',
            password='password123'
        )
        self.user_b = User.objects.create_user(
            email='doctor_user_b@example.com',
            name='User B',
            password='password123'
        )

        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)

        self.list_create_url = reverse('api-doctor-list-create')

    def test_api_no_token_returns_401(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_doctor_creation_and_permission_matrix(self):
        # 1. User A creates Doctor A
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        create_payload = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'experience_years': 20,
            'age': 48,
            'gender': 'M',
            'phone': '555-0199'
        }
        res_create = self.client.post(self.list_create_url, create_payload, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        doctor_id = res_create.data['id']
        self.assertEqual(res_create.data['created_by'], self.user_a.email)

        detail_url = reverse('api-doctor-detail', kwargs={'pk': doctor_id})

        # 2. User B can GET Doctor A (every authenticated user can read)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        res_b_get = self.client.get(detail_url)
        self.assertEqual(res_b_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_b_get.data['name'], 'Gregory House')

        # 3. User B cannot PUT Doctor A -> 403
        update_payload = {
            'name': 'Hacked House',
            'specialization': 'General',
            'experience_years': 5,
            'age': 30,
            'gender': 'M',
            'phone': '555-0000'
        }
        res_b_put = self.client.put(detail_url, update_payload, format='json')
        self.assertEqual(res_b_put.status_code, status.HTTP_403_FORBIDDEN)

        # 4. User B cannot DELETE Doctor A -> 403
        res_b_delete = self.client.delete(detail_url)
        self.assertEqual(res_b_delete.status_code, status.HTTP_403_FORBIDDEN)

        # 5. User A can update Doctor A -> 200
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        res_a_put = self.client.put(detail_url, update_payload, format='json')
        self.assertEqual(res_a_put.status_code, status.HTTP_200_OK)
        self.assertEqual(res_a_put.data['name'], 'Hacked House')

        # 6. User A can delete Doctor A -> 204
        res_a_delete = self.client.delete(detail_url)
        self.assertEqual(res_a_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=doctor_id).exists())


class DoctorBrowserUITests(TestCase):
    def setUp(self):
        self.client_a = Client(SERVER_NAME='localhost')
        self.client_b = Client(SERVER_NAME='localhost')

        self.user_a = User.objects.create_user(
            email='ui_doc_a@example.com',
            name='Doctor Owner',
            password='password123'
        )
        self.user_b = User.objects.create_user(
            email='ui_doc_b@example.com',
            name='Other Staff',
            password='password123'
        )

        self.client_a.force_login(self.user_a)
        self.client_b.force_login(self.user_b)

        self.doctor = Doctor.objects.create(
            name='Allison Cameron',
            specialization='Immunology',
            experience_years=10,
            age=38,
            gender='F',
            phone='555-0202',
            created_by=self.user_a
        )

    def test_doctor_list_view(self):
        # User A sees Doctor with Edit/Delete buttons
        res_a = self.client_a.get(reverse('doctor-list'))
        self.assertEqual(res_a.status_code, 200)
        content_a = res_a.content.decode('utf-8')
        self.assertIn('Dr. Allison Cameron', content_a)
        self.assertIn('Edit', content_a)
        self.assertIn('Delete', content_a)

        # User B sees Doctor with Read Only badge, not edit/delete links
        res_b = self.client_b.get(reverse('doctor-list'))
        self.assertEqual(res_b.status_code, 200)
        content_b = res_b.content.decode('utf-8')
        self.assertIn('Dr. Allison Cameron', content_b)
        self.assertIn('Read Only', content_b)

    def test_non_creator_cannot_access_edit_or_delete_ui(self):
        edit_url = reverse('doctor-edit', kwargs={'pk': self.doctor.pk})
        delete_url = reverse('doctor-delete', kwargs={'pk': self.doctor.pk})

        # Non-creator gets 403 on edit GET and POST
        res_b_edit_get = self.client_b.get(edit_url)
        self.assertEqual(res_b_edit_get.status_code, 403)

        res_b_edit_post = self.client_b.post(edit_url, {'name': 'Hacked'})
        self.assertEqual(res_b_edit_post.status_code, 403)

        # Non-creator gets 403 on delete GET and POST
        res_b_del_get = self.client_b.get(delete_url)
        self.assertEqual(res_b_del_get.status_code, 403)

        res_b_del_post = self.client_b.post(delete_url)
        self.assertEqual(res_b_del_post.status_code, 403)
