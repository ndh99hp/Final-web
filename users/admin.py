from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Country
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'level', 'id_country', 'is_staff', 'is_active')
    list_filter = ('level', 'id_country',
     'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('level', 'id_country', 'avatar')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('level', 'id_country', 'avatar')}),
    )