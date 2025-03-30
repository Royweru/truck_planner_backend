from django.urls import path,include
from .views import TripPlanningView,TripViewSet
from rest_framework.routers import DefaultRouter


# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'', TripViewSet, basename='trip')

urlpatterns = [
   path('plan-trip/', TripPlanningView.as_view(), name='trip-planning'),
   path('',include(router.urls)),
]