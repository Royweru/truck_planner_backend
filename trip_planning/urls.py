from django.urls import path,include
from .views import TripPlanningView,TripViewSet
from rest_framework.routers import DefaultRouter


# Create a router and register our viewset with it
urlpatterns = [
    # Trip planning endpoint
    path('plan-trip/', TripPlanningView.as_view(), name='trip-planning'),
    
    # TripViewSet endpoints written manually
    path('', TripViewSet.as_view({'get': 'list'}), name='trip-list'),
    path('<int:pk>/', TripViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='trip-detail'),
    path('<int:pk>/complete-trip/', TripViewSet.as_view({'post': 'complete_trip'}), name='trip-complete'),
]