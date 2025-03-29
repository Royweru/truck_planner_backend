from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet

urlpatterns = [
    # Specific create route
    path('user/create/', UserViewSet.as_view({'post': 'create'}), name='user-create'),
    
    # JWT Authentication Endpoints
    path('jwt/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Custom user actions
    path('user/me/', UserViewSet.as_view({'get': 'me'}), name='user-profile'),
    path('user/update-profile/', UserViewSet.as_view({'patch': 'update_profile'}), name='user-update-profile'),
]