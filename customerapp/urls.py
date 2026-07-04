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
    path("add_address/", views.add_address, name="add_address"),
    path("edit_address/<int:pk>/",views.edit_address,name="edit_address"),
    path("delete_address/<int:pk>/",views.delete_address,name="delete_address"),
    path("place_order/", views.place_order, name="place_order"),
    path("order_success/", views.order_success, name="order_success"),
    path("orders/", views.orders, name="orders"),
    path("order_details/<int:pk>/",views.order_details,name="order_details"),
    path("cancel_order/<int:pk>/",views.cancel_order,name="cancel_order"),
    path("profile/", views.profile, name="profile"),
    path("save_health_profile/",views.save_health_profile,name="save_health_profile"),
    path("ai-assessment/", views.ai_assessment, name="ai_assessment"),
    path("product/<int:pk>/",views.product_details,name="product_details"),
]
