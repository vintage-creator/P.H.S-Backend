from django.contrib import admin
from .models import CustomUser  # Import your CustomUser model

class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'name', 'phone_number'] 

admin.site.register(CustomUser, CustomUserAdmin)

