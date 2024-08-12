from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from .views import CategoryViewset, PropertyLandlordViewSet, UserViewset, FollowListCreateAPIView, FollowDetailAPIView, \
    PropertyTenantViewSet

r = routers.DefaultRouter()
r.register(r'categories', CategoryViewset)
r.register(r'propertyLandlords', PropertyLandlordViewSet)
r.register(r'users', UserViewset)
r.register(r'propertyTenants', PropertyTenantViewSet)

urlpatterns = [
    path('', include(r.urls)),
    path('follows/', FollowListCreateAPIView.as_view(), name='follow-list-create'),
    path('follows/<int:pk>/', FollowDetailAPIView.as_view(), name='follow-detail'),
]
