import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

def generate_uuid():
    return uuid.uuid4().hex

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=25)
    token_verified = models.BooleanField(default=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True, blank=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number'] 
    def save(self, *args, **kwargs):
        if not self.username: 
            self.username = self.generate_unique_username()
        super().save(*args, **kwargs)

    def generate_unique_username(self):
        # Generate a unique username based on email
        username = f"{uuid.uuid4()}_{self.email.split('@')[0]}"
        # Ensure the generated username is unique
        while CustomUser.objects.filter(username=username).exists():
            username = f"{uuid.uuid4()}_{self.email.split('@')[0]}"
        return username


# Create your models here.
class Handyman(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handyman_services')
    service_name = models.CharField(max_length=100)
    time = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    date = models.DateField()


class ContactForm(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True) 
    image = models.ImageField(upload_to='contact_images/', blank=True, null=True)