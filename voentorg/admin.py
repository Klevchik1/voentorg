# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_available')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'contact_phone')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(OrderStatus)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)