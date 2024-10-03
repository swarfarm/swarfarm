from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# User management stuff
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
