from rest_framework import serializers
from . import models
from django.contrib.auth import get_user_model 

User = get_user_model() 

class handyman_serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Handyman
        fields = '__all__'



class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Use the custom user model
        fields = ['email', 'name', 'phone_number', 'password'] 
        extra_kwargs = {
            'password': {'write_only': True}}
        
    def create(self, validated_data):
        print('Validated Data: %s', validated_data)
        # Remove the password from the validated data
        password = validated_data.pop('password', None)
        # Create the user instance
        user = super(CustomUserCreateSerializer, self).create(validated_data)
        # If a password was provided, set it using set_password to ensure it's hashed
        if password is not None:
            user.set_password(password)
            user.save()
        return user


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactForm
        fields = ['name', 'email', 'message', 'phone_number']