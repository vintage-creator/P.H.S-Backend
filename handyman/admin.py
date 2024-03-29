from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(admin.ModelAdmin):
    model = User
    search_fields = ['email', 'name', 'phone_number'] 

admin.site.register(User, CustomUserAdmin)

