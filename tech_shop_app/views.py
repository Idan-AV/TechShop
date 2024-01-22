from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from google.cloud import storage

from google.oauth2 import id_token
from google.auth.transport import requests

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tech_shop_app.models import *
from tech_shop_app.serializers import *


@api_view(['POST'])
def signup(request):
    s = UserSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(data=s.data)


@api_view(['GET'])
def current_user_details(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data)


@api_view(['GET'])
def get_all_users(request):
    if not request.user.is_authenticated and not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        all_users = User.objects.all()
        serializer = UserSerializer(instance=all_users, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PATCH', 'PUT'])
def get_a_user_by_id(request, user_id):
    if not request.user.is_authenticated and request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'GET':
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        user = get_object_or_404(User, id=user_id)
        serializer = UserUpdateSerializer(
            instance=user, data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)


# works

@api_view(['GET', 'POST'])
def get_all_items(request):
    if request.method == 'GET':
        all_items = Item.objects.all()
        if 'model' in request.query_params:
            all_items = all_items.filter(model__icontains=request.query_params['model'])
        if 'from_price' in request.query_params:
            all_items = all_items.filter(price__gte=request.query_params['from_price'])
        if 'to_price' in request.query_params:
            all_items = all_items.filter(price__lte=request.query_params['to_price'])
        if 'storage' in request.query_params:
            all_items = all_items.filter(storage__iexact=request.query_params['storage'])
        if 'color' in request.query_params:
            all_items = all_items.filter(color__icontains=request.query_params['color'])
        if 'category' in request.query_params:
            all_items = all_items.filter(category__iexact=request.query_params['category'])
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(all_items, request)
        serializer = GetAllItems(instance=result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = AddItem(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


# works good

@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
def get_item_by_id(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'GET':
        serializer = GetItem(instance=item)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = GetItem(
                instance=item, data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data)
    else:
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def get_saved_items_for_user(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        all_saved_items_for_user = SavedItem.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(all_saved_items_for_user, request)
        serializer = GetSavedItems(instance=result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = AddSavedItem(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_items_for_a_company(request, company_name):
    company = get_object_or_404(Company, company_name__iexact=company_name)
    all_cars_by_company = company.item_set.all()
    paginator = PageNumberPagination()
    paginator.page_size = 4
    result_page = paginator.paginate_queryset(all_cars_by_company, request)
    serializer = GetItemsByCompany(instance=result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_saved_item_by_id(request, item_id):
    saved_item = get_object_or_404(SavedItem, item=item_id)
    if request.method == 'GET':
        serializer = GetSavedItem(instance=saved_item)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        serializer = UpdateSavedItem(
            instance=saved_item, data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)
    else:
        saved_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ids_of_saved_items_for_user(request):
    all_saved_ids = list(SavedItem.objects.filter(user=request.user).values_list('item').distinct())
    all_saved_ids = [num for sublist in all_saved_ids for num in sublist]
    print(all_saved_ids)
    return JsonResponse(data=list(all_saved_ids), safe=False)


@api_view(['GET'])
def get_all_companies(request):
    companies = Company.objects.all()
    serializer = GetAllCompanies(instance=companies, many=True)
    return Response(serializer.data)