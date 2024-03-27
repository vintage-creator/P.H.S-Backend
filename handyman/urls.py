from django.urls import path
from .views import handymanListCreateAPIView, handymanRetrieveUpdateAPIView, contact_form, forgot_password, verify_token, reset_password, GoogleLogin

urlpatterns = [
    path('accounts/google/login/callback/', GoogleLogin.as_view(), name='google_login'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-token/', verify_token, name='verify_token'),
    path('reset-password/', reset_password, name='reset_password'),
    path('contact/', contact_form, name='contact_form'),
    path('api/phs/', handymanListCreateAPIView.as_view(), name='handyman-list-create'),
    path('api/phs/<int:pk>/', handymanRetrieveUpdateAPIView.as_view(), name='handyman-retrieve-update'),
]