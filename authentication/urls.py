
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as authentication_views
from authentication import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
   
    # path("account/", include(auth_urlpatterns)),  # new
    path('login/', views.login_view, name="login"),

    path('FIDO/', views.fido_authentication, name="FIDO_Login"),
    
    path('Password/', views.password_authentication, name="Password_Login"),
    path("register/", views.register_new_user, name="register"),
    path("register_additional_info/", views.register_new_user_additionalInfo, name="register_new_user_info"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path('OTP/', views.otp_authentication, name='otp_login'),
    path('OTP/<str:uid>/', views.otp_verify, name='otp'),
    path('authentication_method/',views.authentication_method,name='auth_meth'),
    path('preferred_authentication_method/',views.choose_authentication_method,name='preferred_auth_meth'),
    



]
