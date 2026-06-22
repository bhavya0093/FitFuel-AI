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
from . import views

urlpatterns = [
    path("customer-dashboard/",views.customer_dashboard,name="customer_dashboard"),
    path("logout/",views.logout,name="logout"),
    path("edit_profile/",views.edit_profile,name="edit_profile"),
    path("show_product/",views.show_product,name="show_product"),
    path("add_to_cart/<int:pk>",views.add_to_cart,name="add_to_cart"),
    path("view_cart/",views.view_cart,name="view_cart"),
    path("checkout/",views.checkout,name="checkout"),
    path("payment/",views.payment,name="payment"),
    path("increase_qty/<int:pk>/", views.increase_qty, name="increase_qty"),
    path("decrease_qty/<int:pk>/", views.decrease_qty, name="decrease_qty"),
]
