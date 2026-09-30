from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Patient

User = get_user_model()


class PatientAPITests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email='doctor_a@example.com',
            name='Doctor A',
            password='password123'
        )
        self.user_b = User.objects.create_user(
            email='doctor_b@example.com',
            name='Doctor B',
            password='password123'
        )

        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)

        self.list_create_url = reverse('api-patient-list-create')

    def test_api_no_token_returns_401(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_user_a_creates_patient(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        payload = {
            'name': 'John Patient',
            'email': 'john@example.com',
            'age': 35,
            'gender': 'M',
            'phone': '555-0199'
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Patient')
        self.assertEqual(response.data['created_by'], self.user_a.email)

    def test_api_user_isolation_and_scoping(self):
        patient_a = Patient.objects.create(
            name='Alice A',
            email='alice@example.com',
            age=28,
            gender='F',
            phone='555-0101',
            created_by=self.user_a
        )
        detail_url = reverse('api-patient-detail', kwargs={'pk': patient_a.pk})

        # User A lists -> sees patient
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        res_a_list = self.client.get(self.list_create_url)
        self.assertEqual(res_a_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_a_list.data), 1)

        # User B lists -> does NOT see User A's patient
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        res_b_list = self.client.get(self.list_create_url)
        self.assertEqual(res_b_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_b_list.data), 0)

        # User B GET User A's patient -> 404
        res_b_get = self.client.get(detail_url)
        self.assertEqual(res_b_get.status_code, status.HTTP_404_NOT_FOUND)

        # User B PUT User A's patient -> 404
        update_payload = {
            'name': 'Hacked Alice',
            'email': 'alice@example.com',
            'age': 30,
            'gender': 'F',
            'phone': '555-9999'
        }
        res_b_put = self.client.put(detail_url, update_payload, format='json')
        self.assertEqual(res_b_put.status_code, status.HTTP_404_NOT_FOUND)

        # User B DELETE User A's patient -> 404
        res_b_delete = self.client.delete(detail_url)
        self.assertEqual(res_b_delete.status_code, status.HTTP_404_NOT_FOUND)

        # User A PUT own patient -> 200
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        res_a_put = self.client.put(detail_url, update_payload, format='json')
        self.assertEqual(res_a_put.status_code, status.HTTP_200_OK)
        self.assertEqual(res_a_put.data['name'], 'Hacked Alice')

        # Invalid age -> 400
        invalid_age_payload = {
            'name': 'Valid Name',
            'email': 'valid@example.com',
            'age': 200,
            'gender': 'F',
            'phone': '555-0101'
        }
        res_invalid_age = self.client.post(self.list_create_url, invalid_age_payload, format='json')
        self.assertEqual(res_invalid_age.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid gender -> 400
        invalid_gender_payload = {
            'name': 'Valid Name',
            'email': 'valid@example.com',
            'age': 30,
            'gender': 'X',
            'phone': '555-0101'
        }
        res_invalid_gender = self.client.post(self.list_create_url, invalid_gender_payload, format='json')
        self.assertEqual(res_invalid_gender.status_code, status.HTTP_400_BAD_REQUEST)

        # User A DELETE own patient -> 204
        res_a_delete = self.client.delete(detail_url)
        self.assertEqual(res_a_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=patient_a.pk).exists())
