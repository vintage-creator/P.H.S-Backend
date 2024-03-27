from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from rest_framework import generics
from .models import Handyman
from .permissions import CustomPermission
from .serializers import handyman_serializer, ContactFormSerializer
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils.data_access import get_handyman_user_info
from .utils.custom_token_gen import custom_token_generator
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


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
            send_mail(subject, message, from_email, [to_email], fail_silently=False)
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

            # Send email
            subject = 'New Contact Form Submission'
            email_message = f"""
            Name: {data['name']}
            Email: {data['email']}
            Message: {data['message']}
            Phone Number: {data.get('phone_number', '')}
            """

            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                ["chuksy3@gmail.com"],
                fail_silently=False,
            )

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
            send_mail(
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




