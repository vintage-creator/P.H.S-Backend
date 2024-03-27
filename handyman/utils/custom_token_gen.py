import random
import string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include the user's primary key and a timestamp in the hash value
        return str(user.pk) + str(timestamp)

    def make_random_token(self):
        # Generate a random 6-character token using uppercase letters and digits
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(6))

custom_token_generator = CustomTokenGenerator()
