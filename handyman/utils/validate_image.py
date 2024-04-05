from django.core.exceptions import ValidationError

def validate_image_file_size(value):
    limit = 2 * 1024 * 1024  # 2MB limit
    if value.size > limit:
        raise ValidationError('Image file too large ( > 2MB )')
