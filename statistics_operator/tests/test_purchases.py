from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from statistics_operator.models import Customer, Purchase, User
from datetime import datetime, timedelta
from django.utils import timezone


class PurchaseViewSetTests(APITestCase):

    def setUp(self):
        Purchase.objects.all().delete()   
        Customer.objects.all().delete()   
        User.objects.all().delete()       

        self.admin_user = User.objects.create_superuser(username='adminuser', password='password')
        self.regular_user = User.objects.create_user(username='regularuser', password='password')

        self.customer1 = Customer.objects.create(username='user1', total_spent=100.00, date_joined='2022-01-01')
        self.customer2 = Customer.objects.create(username='user2', total_spent=0.00, date_joined='2022-01-02')
        self.customer3 = Customer.objects.create(username='user3', total_spent=200.00, date_joined='2022-01-03')

        self.purchase1 = Purchase.objects.create(
            customer=self.customer1,
            book_id=1,
            book_title="Book 1",
            status="processed",
            purchase_price=50.00,
            purchase_date=timezone.now() - timedelta(days=1)
        )
        self.purchase2 = Purchase.objects.create(
            customer=self.customer2,
            book_id=2,
            book_title="Book 2",
            status="pending",
            purchase_price=30.00,
            purchase_date=timezone.now()
        )
        self.purchase3 = Purchase.objects.create(
            customer=self.customer3,
            book_id=3,
            book_title="Book 3",
            status="delivered",
            purchase_price=100.00,
            purchase_date=timezone.now() - timedelta(days=30)
        )

        self.admin_token = str(AccessToken.for_user(self.admin_user))
        self.client = APIClient()
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

    def test_get_all_purchases(self):
        url = reverse('purchases-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_purchases_filtered_by_status(self):
        url = reverse('purchases-list')

        response = self.client.get(url, {'status': 'processed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'processed')

    def test_get_purchases_filtered_by_nonexistent_status(self):
        url = reverse('purchases-list')

        response = self.client.get(url, {'status': 'shipped'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_purchases_for_current_month(self):
        url = reverse('purchases-current-month')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_purchases_by_month(self):
        url = reverse('purchases-by-month')

        response = self.client.get(url, {'month': timezone.now().month})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(url, {'month': (timezone.now() - timedelta(days=30)).month})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_purchases_by_date(self):
        url = reverse('purchases-by-date')
        date_str = timezone.now().strftime('%Y-%m-%d')

        response = self.client.get(url, {'date': date_str})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        response = self.client.get(url, {'date': '2022-13-01'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)