from django.contrib import admin
from statistics_operator.models import Customer, Purchase, OrderItemData


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'username', 'phone_number', 'total_spent', 'date_joined')
    search_fields = ('username', 'phone_number')
    list_filter = ('date_joined',)
    ordering = ('-total_spent',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_id', 'customer', 'status', 'purchase_date', 'purchase_price') 
    search_fields = ('customer__username',) 
    list_filter = ('status', 'purchase_date')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)


@admin.register(OrderItemData)
class OrderItemDataAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_title', 'quantity', 'price', 'discount', 'total_price', 'purchase_date')
    search_fields = ('book_title', 'book_id')  
    list_filter = ('purchase_date',) 
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',) 
