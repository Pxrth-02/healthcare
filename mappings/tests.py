from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from doctors.models import Doctor
from patients.models import Patient
from .models import PatientDoctorMapping

User = get_user_model()


class MappingCrossOwnerTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email='map_user_a@example.com',
            name='User A',
            password='password123'
        )
        self.user_b = User.objects.create_user(
            email='map_user_b@example.com',
            name='User B',
            password='password123'
        )

        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)

        # Create Patient A and Patient B
        self.patient_a = Patient.objects.create(
            name='Patient A',
            email='patient_a@example.com',
            age=30,
            gender='M',
            phone='111-1111',
            created_by=self.user_a
        )
        self.patient_b = Patient.objects.create(
            name='Patient B',
            email='patient_b@example.com',
            age=40,
            gender='F',
            phone='222-2222',
            created_by=self.user_b
        )

        # Create Doctor A and Doctor B
        self.doctor_a = Doctor.objects.create(
            name='Doctor A',
            specialization='Cardiology',
            experience_years=10,
            age=45,
            gender='M',
            phone='333-3333',
            created_by=self.user_a
        )
        self.doctor_b = Doctor.objects.create(
            name='Doctor B',
            specialization='Neurology',
            experience_years=12,
            age=48,
            gender='F',
            phone='444-4444',
            created_by=self.user_b
        )

        self.list_create_url = reverse('api-mapping-list-create')

    def test_required_cross_owner_rules(self):
        # 1. A maps A's patient -> A's doctor: success
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        res1 = self.client.post(self.list_create_url, {
            'patient': self.patient_a.id,
            'doctor': self.doctor_a.id
        }, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        mapping_a_a_id = res1.data['id']
        self.assertEqual(res1.data['doctor']['name'], self.doctor_a.name)

        # 2. A maps A's patient -> B's doctor: success
        res2 = self.client.post(self.list_create_url, {
            'patient': self.patient_a.id,
            'doctor': self.doctor_b.id
        }, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        mapping_a_b_id = res2.data['id']
        self.assertEqual(res2.data['doctor']['name'], self.doctor_b.name)

        # 3. A maps B's patient -> A's doctor: rejected (400)
        res3 = self.client.post(self.list_create_url, {
            'patient': self.patient_b.id,
            'doctor': self.doctor_a.id
        }, format='json')
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

        # 4. duplicate A patient + A/B doctor pair: rejected (400)
        res4 = self.client.post(self.list_create_url, {
            'patient': self.patient_a.id,
            'doctor': self.doctor_a.id
        }, format='json')
        self.assertEqual(res4.status_code, status.HTTP_400_BAD_REQUEST)

        # 5. A GET /mappings/ does not see B's patient mappings
        # Let User B map Patient B to Doctor B
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        res_b_create = self.client.post(self.list_create_url, {
            'patient': self.patient_b.id,
            'doctor': self.doctor_b.id
        }, format='json')
        self.assertEqual(res_b_create.status_code, status.HTTP_201_CREATED)
        mapping_b_b_id = res_b_create.data['id']

        # Now User A checks /api/mappings/
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}')
        res_a_list = self.client.get(self.list_create_url)
        self.assertEqual(res_a_list.status_code, status.HTTP_200_OK)
        a_mapping_ids = [m['id'] for m in res_a_list.data]
        self.assertIn(mapping_a_a_id, a_mapping_ids)
        self.assertIn(mapping_a_b_id, a_mapping_ids)
        self.assertNotIn(mapping_b_b_id, a_mapping_ids)

        # 6. A GET /mappings/B_patient_id/ -> 404
        b_patient_url = reverse('api-mapping-detail', kwargs={'pk': self.patient_b.id})
        res6 = self.client.get(b_patient_url)
        self.assertEqual(res6.status_code, status.HTTP_404_NOT_FOUND)

        # A GET /mappings/A_patient_id/ -> 200 (sees mappings for patient A)
        a_patient_url = reverse('api-mapping-detail', kwargs={'pk': self.patient_a.id})
        res_a_patient = self.client.get(a_patient_url)
        self.assertEqual(res_a_patient.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_a_patient.data), 2)

        # 7. B DELETE A's mapping -> 404
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}')
        delete_url_a_a = reverse('api-mapping-detail', kwargs={'pk': mapping_a_a_id})
        res7 = self.client.delete(delete_url_a_a)
        self.assertEqual(res7.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=mapping_a_a_id).exists())

        # 8. deleting a patient removes its mappings
        patient_a_map_count = PatientDoctorMapping.objects.filter(patient=self.patient_a).count()
        self.assertGreater(patient_a_map_count, 0)
        self.patient_a.delete()
        self.assertEqual(PatientDoctorMapping.objects.filter(patient_id=self.patient_a.id).count(), 0)

        # 9. deleting a doctor removes its mappings
        # Check mapping for B
        self.assertEqual(PatientDoctorMapping.objects.filter(doctor=self.doctor_b).count(), 1)
        self.doctor_b.delete()
        self.assertEqual(PatientDoctorMapping.objects.filter(doctor_id=self.doctor_b.id).count(), 0)
