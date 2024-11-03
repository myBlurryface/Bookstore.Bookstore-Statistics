from rest_framework import serializers
from statistics_operator.models import *

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['customer_id', 'username', 'total_spent', 'date_joined'] 


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

