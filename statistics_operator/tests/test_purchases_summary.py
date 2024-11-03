from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from statistics_operator.models import Customer, Purchase, User
from datetime import datetime, timedelta
from django.utils import timezone


class PurchaseStatsViewTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password')
        self.regular_user = User.objects.create_user(username='regularuser', password='password')

        self.customer = Customer.objects.create(username='user1', total_spent=100.00, date_joined='2022-01-01')

        self.purchase1 = Purchase.objects.create(
            customer=self.customer,
            book_id=1,
            book_title='Book One',
            status='delivered',
            purchase_price=10.00,
            purchase_date=timezone.make_aware(datetime(2024, 11, 1, 10, 0, 0))  
        )
        self.purchase2 = Purchase.objects.create(
            customer=self.customer,
            book_id=2,
            book_title='Book Two',
            status='delivered',
            purchase_price=15.00,
            purchase_date=timezone.make_aware(datetime(2024, 11, 1, 15, 0, 0))
        )

        self.purchase3 = Purchase.objects.create(
            customer=self.customer,
            book_id=1,
            book_title='Book One',
            status='delivered',
            purchase_price=10.00,
            purchase_date=timezone.make_aware(datetime(2024, 7, 15, 15, 0, 0))   
        )
        self.purchase4 = Purchase.objects.create(
            customer=self.customer,
            book_id=2,
            book_title='Book Two',
            status='delivered',
            purchase_price=20.00,
            purchase_date=timezone.make_aware(datetime(2024, 8, 20, 15, 0, 0))   
        )

        self.purchase5 = Purchase.objects.create(
            customer=self.customer,
            book_id=2,
            book_title='Book Two',
            status='delivered',
            purchase_price=20.00,
            purchase_date=timezone.make_aware(datetime(2024, 8, 20, 15, 0, 0))   
        )

        self.purchase6 = Purchase.objects.create(
            customer=self.customer,
            book_id=3,
            book_title='Book Three',
            status='delivered',
            purchase_price=15.00,
            purchase_date=timezone.make_aware(datetime(2024, 9, 10, 10, 0, 0))  
        )

        self.admin_token = str(AccessToken.for_user(self.admin_user))
        self.client = APIClient()
        self.api_authentication()

        self.url_template = '/summary/get_summary/' 

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

    def test_get_stats_specific_date(self):
        url = f"{self.url_template}?period=specific_date&date=2024-11-01"  

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['top_book'], 'Book One')   
        self.assertEqual(response.data['total_sales'], 25.00)   

        self.assertEqual(response.data['avg_check'], 12.50)  

    def test_get_current_quarter_stats(self):
        url = f"{self.url_template}?period=this_quarter" 

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_book', response.data)   
        self.assertIn('total_sales', response.data)   
        self.assertIn('avg_check', response.data)   

    def test_get_stats_last_quarter(self):
        url = f"{self.url_template}?period=last_quarter"   

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_book', response.data)   
        self.assertIn('total_sales', response.data)
        self.assertIn('avg_check', response.data)  

        self.assertEqual(response.data['top_book'], 'Book Two') 
        self.assertEqual(response.data['total_sales'], 65.00)  
        self.assertEqual(response.data['avg_check'], 16.25)  

    def test_invalid_period(self):
        url = f"{self.url_template}?period=invalid_period" 

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid period specified.')  