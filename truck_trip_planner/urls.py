
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/trips/',include('trip_planning.urls')),
    path('api/auth/', include('users.urls')),
]
