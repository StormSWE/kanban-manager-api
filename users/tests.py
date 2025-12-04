from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserEndpointsTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="existing@example.com", password="StrongPass123")

	def test_register_user(self):
		url = reverse("users:user-register")
		payload = {
			"email": "new@example.com",
			"password": "StrongPass123",
			"confirm_password": "StrongPass123",
			"name": "New User",
		}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn("access", response.data)

	def test_login_user(self):
		url = reverse("users:user-login")
		payload = {"email": "existing@example.com", "password": "StrongPass123"}
		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access", response.data)

	def test_profile_requires_auth(self):
		url = reverse("users:user-profile")
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
