from django.urls import path
from .views import (
    customer_create_ticket,
    customer_dashboard,
    customer_change_password,
    customer_profile_settings,
    customer_login,
    customer_logout,
    home,
    login_page,
    site_content_api,
)

urlpatterns = [
    path('', home, name='home'),
    path('api/site-content/', site_content_api, name='site_content_api'),
    path('login/', login_page, name='login'),
    path('customer/login/', customer_login, name='customer_login'),
    path('customer/logout/', customer_logout, name='customer_logout'),
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('customer/profile/', customer_profile_settings, name='customer_profile_settings'),
    path('customer/tickets/new/', customer_create_ticket, name='customer_create_ticket'),
    path('customer/password/', customer_change_password, name='customer_change_password'),
]
