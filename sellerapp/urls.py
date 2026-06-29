"""
URL configuration for bkshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('logout/', logout, name='logout'),
    path('update_profile/', update_profile, name='update_profile'),
    path('add_product/', add_product, name='add_product'),
    path('view_product/', view_product, name='view_product'),
    path('edit_product/<int:pid>/', edit_product, name='edit_product'),
    path('delete_product/<int:pid>/', delete_product, name='delete_product'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('change_password/', change_password, name='change_password'),
    path('resend-otp/<str:email>/',resend_otp,name='resend_otp'),
    path('view_categories/', view_categories, name='view_categories'),
    path('add_category/', add_category, name='add_category'),
    path('edit_category/<int:cid>/', edit_category, name='edit_category'),
    path('delete_category/<int:cid>/', delete_category, name='delete_category'),
    path("admin_orders/",admin_orders,name="admin_orders"),
    path("admin_order_details/<int:pk>/",admin_order_details,name="admin_order_details"),
]

