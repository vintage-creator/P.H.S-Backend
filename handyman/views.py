from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from rest_framework import generics
from .models import Handyman
from .permissions import CustomPermission
from .serializers import handyman_serializer, ContactFormSerializer
from django.core.mail import EmailMessage
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from .utils.data_access import get_handyman_user_info
from .utils.custom_token_gen import custom_token_generator
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.core.exceptions import ValidationError
from .utils.validate_image import validate_image_file_size


User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response_data(self, user):
        try:
            social_account = SocialAccount.objects.get(user=user)
            profile_name = social_account.extra_data.get('name', '')
            return {'profile_name': profile_name}
        except SocialAccount.DoesNotExist:
            return {'error': 'Social account not found'}

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        response_data = self.get_response_data(self.user)
        return Response(response_data)


class handymanListCreateAPIView(generics.ListCreateAPIView):
    queryset = Handyman.objects.all()
    serializer_class = handyman_serializer
    permission_classes = [CustomPermission]

    def perform_create(self, serializer):
        handyman_instance = serializer.save()
        self.send_handyman_info_email(handyman_instance.id, 'chuksy3@gmail.com')

    def send_handyman_info_email(self, handyman_id, to_email):
        handyman, user = get_handyman_user_info(handyman_id)
        if handyman and user:
            subject = 'Handyman Service Details'
            message = f"""
            Hello,

            Here are the details of the Handyman service a client requested:

            Service Name: {handyman.service_name}
            Time: {handyman.time}
            Address: {handyman.address}
            Date: {handyman.date}

            Requested by:
            Name: {user.name}
            Email: {user.email}
            Phone: {user.phone_number}
            """

            from_email =  settings.DEFAULT_FROM_EMAIL
            EmailMessage(subject, message, from_email, [to_email], fail_silently=False)
            print("Email sent!")


class handymanRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Handyman.objects.all()
    serializer_class = handyman_serializer
    permission_classes = [CustomPermission]


@api_view(['POST'])
def contact_form(request):
    if request.method == 'POST':
        serializer_class = ContactFormSerializer
        serializer = serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data

            # Prepare email message
            subject = 'New Contact Form Submission'
            email_message = f"""
            <p><strong>Name:</strong> {data['name']}</p>
            <p><strong>Email:</strong> {data['email']}</p>
            <p><strong>Message:</strong> {data['message']}</p>
            <p><strong>Phone Number:</strong> {data.get('phone_number', '')}</p>
            """

            # Check if an image is attached
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                try:
                    # Validate the image size
                    validate_image_file_size(image_file)
                except ValidationError as e:
                    return Response({'error': str(e)}, status=400)
                
                email_message += """
                <p>This customer is making an inquiry. Attached is the image:</p>
                """

                # Create EmailMessage instance
                email = EmailMessage(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ["chuksy3@gmail.com"],
                )

                # Attach image if provided
                if 'image' in request.FILES:
                    image_file = request.FILES['image']
                    email.attach(image_file.name, image_file.read(), image_file.content_type)

                # Send email
                email.content_subtype = 'html'
                email.send(fail_silently=False)

            return Response({'message': 'Your message has been sent.'})
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email address is required.'}, status=400)
    
    try:
        user = User.objects.get(email=email)
        token = custom_token_generator.make_random_token()
        if hasattr(user, 'password_reset_token'):
            user.password_reset_token = token
            user.save()
        try:
            EmailMessage(
                'Password Reset Request',
                f'Use this token to reset your password: {token}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'A password reset token has been sent.', 'user_id': user.pk})
        except Exception as e:
            print(f"Error sending email: {e}")
            return Response({'error': 'Failed to send password reset token. Please try again.'}, status=500)
    except User.DoesNotExist:
        return Response({'message': 'If an account with that email exists, a password reset token has been sent.'})


@api_view(['POST'])
def verify_token(request):
    user_id = request.data.get('user_id')  
    token = request.data.get('token')

    if not user_id:
        return Response({'error': 'User ID is required.'}, status=400)

    if not token:
        return Response({'error': 'Token is required.'}, status=400)
    
    try:
        user = User.objects.get(pk=user_id)
        if user.password_reset_token == token:
            user.token_verified = True
            user.save()
            return Response({'success': 'Token is valid.'})
        else:
            return Response({'error': 'Token is invalid or expired.'}, status=400)
    except (User.DoesNotExist, ValueError, AttributeError):
        return Response({'error': 'Invalid token.'}, status=404)


@api_view(['POST'])
def reset_password(request):
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    user_id = request.data.get('user_id')

    if not new_password and not confirm_password:
        return Response({'error': 'New password is required.'}, status=400)
    if not confirm_password:
        return Response({'error': 'Confirm password is required.'}, status=400)
    if not user_id:
        return Response({'error': 'User ID is required.'}, status=400)

    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=400)

    try:
        user = User.objects.get(pk=user_id)

        if user.token_verified:
           user.set_password(new_password)
           user.password_reset_token = None
           user.save()
           return Response({'success': 'Password has been reset successfully.'})
        else:
            return Response({'error': 'Token not verified. Please verify your token.'}, status=400)
    except (ValueError, TypeError, User.DoesNotExist):
        return Response({'error': 'Invalid user ID or token.'}, status=400)




