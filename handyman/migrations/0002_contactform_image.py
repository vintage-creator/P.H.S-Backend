# Generated by Django 5.0.3 on 2024-04-05 06:11

import handyman.utils.validate_image
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handyman', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactform',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='contact_images/', validators=[handyman.utils.validate_image.validate_image_file_size]),
        ),
    ]
