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
]

