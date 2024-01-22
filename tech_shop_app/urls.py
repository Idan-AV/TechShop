from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from tech_shop_app.views import *


urlpatterns = [
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/refresh', TokenRefreshView.as_view()),
    path('auth/signup', signup),
    path('auth/get_all_users', get_all_users),
    path('auth/current_user_details', current_user_details),
    path('auth/get_a_user_by_name/<int:user_id>', get_a_user_by_id),
    path('get_item_by_id/<int:item_id>', get_item_by_id),
    path('all_items', get_all_items),
    path('saved_items', get_saved_items_for_user),
    path('items_according_a_company/<str:company_name>', get_all_items_for_a_company),
    path('get_saved_item_by_id/<int:item_id>', get_saved_item_by_id),
    path('get_all_saved_ids_for_user', get_ids_of_saved_items_for_user),
    path('gel_all_companies', get_all_companies)

]

