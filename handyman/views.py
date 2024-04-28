from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from rest_framework import generics, status
from .models import Handyman
from .permissions import CustomPermission
from .serializers import handyman_serializer, ContactFormSerializer, AppointmentSerializer
from django.core.mail import EmailMessage
from rest_framework.decorators import api_view
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
from datetime import datetime


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
    permission_classes = [CustomPermission]

    def perform_create(self, serializer):
        handyman_instance = serializer.save()
        handyman, user = get_handyman_user_info(handyman_instance.id)
        if handyman and user:
            self.send_admin_handyman_info_email(handyman, user, 'princehandymanservices01@gmail.com')
            self.send_user_confirmation_email(handyman, user)

    def send_admin_handyman_info_email(self, handyman, user, admin_email):
        subject = 'New Handyman Service Request'
        message = f"""
        <p>Hello Admin,</p>
        <p>A new handyman service has been requested. Here are the details:</p>
        <p>Service Name: {handyman.service_name}</p>
        <p>Time: {handyman.time}</p>
        <p>Address: {handyman.address}</p>
        <p>Date: {handyman.date}</p>
        <p>Requested by:</p>
        <p>Name: {user.name}</p>
        <p>Email: {user.email}</p>
        <p>Phone: {user.phone_number}</p>
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        email_message = EmailMessage(subject, message, from_email, [admin_email])
        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)
        print("Admin notification email sent!")

    def send_user_confirmation_email(self, handyman, user):
        subject = 'Handyman Service Request Confirmation'
        message = f"""
        <p>Dear {user.name},</p>
        <p>We have received your request for our handyman service. Here are the details:</p>
        <p>Service Name: {handyman.service_name}</p>
        <p>Time: {handyman.time}</p>
        <p>Address: {handyman.address}</p>
        <p>Date: {handyman.date}</p>
        <p>We will reach out to you soon to confirm the details and finalize the arrangements.</p>
        <p>Thank you for choosing our services!</p>
        <p>Best Regards,</p>
        <p>PHS HQ</p>
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        email_message = EmailMessage(subject, message, from_email, [user.email])
        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)
        print("User confirmation email sent!")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return handyman_serializer
        return AppointmentSerializer

    
    def get(self, request, *args, **kwargs):
        time_slots = [
            "08:00AM", "09:00AM", "10:00AM",
            "11:00AM", "12:00PM", "01:00PM",
            "02:00PM", "03:00PM", "04:00PM",
            "05:00PM", "06:00PM", "07:00PM"
        ]

        current_date = datetime.now().date()
        current_time = datetime.now().time()

        # Convert time slots to datetime objects
        available_time_slots = [datetime.strptime(time_slot, '%I:%M%p').time() for time_slot in time_slots]

        filtered_time_slots = []

        # Include time slots from current time onwards
        for time_slot in available_time_slots:
            if current_time <= time_slot:
                filtered_time_slots.append(time_slot.strftime('%I:%M%p'))

        # Filter out time slots not in filtered_time_slots
        remaining_time_slots = [time_slot.strftime('%I:%M%p') for time_slot in available_time_slots if time_slot.strftime('%I:%M%p') not in filtered_time_slots]

        # Construct response data with date and time for available time slots
        response_data = [{'date': current_date.strftime('%Y-%m-%d'), 'time': time} for time in remaining_time_slots]
        
        # Filter user bookings made on the current date
        user_bookings = self.get_queryset().filter(date=current_date)

        # Serialize user bookings
        user_bookings_serializer = self.get_serializer(user_bookings, many=True)
        
        # Combine available time slots and user bookings
        response_data += user_bookings_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)


class handymanRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Handyman.objects.all()
    serializer_class = handyman_serializer
    permission_classes = [CustomPermission]


@api_view(['POST'])
def contact_form(request):
    if request.method == 'POST':
        serializer = ContactFormSerializer(data=request.data)

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
            
            # Initialize the EmailMessage instance
            email = EmailMessage(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                ['princehandymanservices01@gmail.com'],
            )
            email.content_subtype = 'html' 
            # Check if an image is attached
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                try:
                    validate_image_file_size(image_file)
                    pass
                except ValidationError as e:
                    return Response({'error': str(e)}, status=400)
                
                email_message += """
                <p>This customer is making an inquiry. Attached is the image:</p>
                """
                
                # Attach the image
                email.attach(image_file.name, image_file.read(), image_file.content_type)

            # Send email
            email.send(fail_silently=False)

            return Response({'message': 'Your message has been sent.'})
    else:
        return Response({'error': 'Invalid request'}, status=400)
    

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
            email_message = EmailMessage(
                'Password Reset Request',
                f'Use this token to reset your password: {token}',
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            email_message.send(fail_silently=False) 
            return Response({'message': 'A password reset token has been sent.', 'user_id': user.pk})
        except Exception as e:
            print(f"Error sending email: {e}")
            return Response({'error': 'Failed to send password reset token. Please try again.'}, status=500)
    except User.DoesNotExist:
        return Response({'error': 'User not found!'}, status=404)
    

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

    if not new_password or not confirm_password:
        return Response({'error': 'Both new password and confirm password are required.'}, status=400)
    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=400)
    if not user_id:
        return Response({'error': 'User ID is required.'}, status=400)

    try:
        user = User.objects.get(pk=user_id)

        if user.token_verified:
            user.set_password(new_password)
            user.password_reset_token = None
            user.save()

            html_content = f"""
            <p>Hello {user.name},</p>
            <p>Your password has been successfully reset.</p>
            <p>If you did not perform this action, please contact our support team immediately.</p>
            """
            email_message = EmailMessage(
                'Password Reset Successful',
                html_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email_message.content_subtype = "html" 
            email_message.send(fail_silently=False) 

            return Response({'success': 'Password has been reset successfully.'})
        else:
            return Response({'error': 'Token not verified. Please verify your token.'}, status=400)
    except (ValueError, TypeError, User.DoesNotExist):
        return Response({'error': 'Invalid user ID or token.'}, status=400)




