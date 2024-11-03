from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from statistics_operator.models import Customer

class CustomerViewSetTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password')

        self.customer1 = Customer.objects.create(username='user1', total_spent=100.00, date_joined='2022-01-01')
        self.customer2 = Customer.objects.create(username='user2', total_spent=0.00, date_joined='2022-01-02')
        self.customer3 = Customer.objects.create(username='user3', total_spent=200.00, date_joined='2022-01-03')

        self.admin_token = str(AccessToken.for_user(self.admin_user))

        self.client = APIClient()

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_all_customers(self):
        self.api_authentication(self.admin_token)

        url = reverse('customers-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  

    def test_get_customers_sorted_by_date(self):
        self.api_authentication(self.admin_token)

        url = reverse('customers-list')

        response = self.client.get(url, {'ordering': '-date_joined'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'user3')

    def test_get_customers_sorted_by_total_spent(self):
        self.api_authentication(self.admin_token)

        url = reverse('customers-list')

        response = self.client.get(url, {'ordering': '-total_spent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'user3')

    def test_get_total_spent(self):
        self.api_authentication(self.admin_token)

        url = reverse('customers-total-users') 

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_users'], 3)
        self.assertEqual(response.data['users_with_zero_spent'], 1)
        self.assertEqual(response.data['users_with_spent'], 2)
