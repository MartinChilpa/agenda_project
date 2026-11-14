from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Appointment, Customer, ServiceType

User = get_user_model()


class AgendaWorkspaceIsolationTests(APITestCase):
    def setUp(self):
        self.provider_a = User.objects.create_user(
            username='lashista',
            password='secret123',
            role='PROVIDER',
        )
        self.provider_b = User.objects.create_user(
            username='peluquero',
            password='secret123',
            role='PROVIDER',
        )
        self.client_user = User.objects.create_user(
            username='cliente',
            password='secret123',
            role='CLIENT',
        )
        self.service_a = ServiceType.objects.create(provider=self.provider_a, name='Pestañas')
        self.service_b = ServiceType.objects.create(provider=self.provider_b, name='Corte')
        self.customer_a = Customer.objects.create(provider=self.provider_a, name='Ana')
        self.customer_b = Customer.objects.create(provider=self.provider_b, name='Beatriz')

    def test_customer_is_created_inside_authenticated_provider_workspace(self):
        self.client.force_authenticate(self.provider_a)

        response = self.client.post(reverse('customer-list'), {'name': 'Carla'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['provider'], self.provider_a.pk)
        self.assertTrue(Customer.objects.filter(provider=self.provider_a, name='Carla').exists())

    def test_provider_only_sees_own_customers(self):
        self.client.force_authenticate(self.provider_a)

        response = self.client.get(reverse('customer-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([customer['id'] for customer in response.data], [self.customer_a.pk])

    def test_provider_cannot_use_another_workspace_customer(self):
        self.client.force_authenticate(self.provider_a)

        response = self.client.post(
            reverse('appointment-list'),
            {
                'customer': self.customer_b.pk,
                'service_type': self.service_a.pk,
                'date': '2026-11-10',
                'start_time': '09:00:00',
                'end_time': '10:00:00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_time_is_available_to_different_providers(self):
        Appointment.objects.create(
            provider=self.provider_a,
            customer=self.customer_a,
            service_type=self.service_a,
            date='2026-11-10',
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        appointment_b = Appointment(
            provider=self.provider_b,
            customer=self.customer_b,
            service_type=self.service_b,
            date='2026-11-10',
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        appointment_b.full_clean()

    def test_overlapping_time_is_rejected_for_same_provider(self):
        Appointment.objects.create(
            provider=self.provider_a,
            customer=self.customer_a,
            service_type=self.service_a,
            date='2026-11-10',
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        overlapping = Appointment(
            provider=self.provider_a,
            customer=self.customer_a,
            service_type=self.service_a,
            date='2026-11-10',
            start_time=time(9, 30),
            end_time=time(10, 30),
        )

        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_client_role_cannot_manage_an_agenda(self):
        self.client.force_authenticate(self.client_user)

        response = self.client.get(reverse('appointment-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
