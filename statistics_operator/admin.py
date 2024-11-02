from django.contrib import admin
from .models import Customer, Purchase


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'username', 'phone_number', 'total_spent', 'date_joined')
    search_fields = ('username', 'phone_number')
    list_filter = ('date_joined',)
    ordering = ('-total_spent',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_id', 'customer', 'book_title', 'status', 'purchase_date', 'purchase_price')
    search_fields = ('book_title', 'customer__username')
    list_filter = ('status', 'purchase_date')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)
