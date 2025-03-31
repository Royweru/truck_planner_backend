from rest_framework import serializers
from .models import Trip, ELDLog, RouteStop
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']
        
class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = '__all__'
        read_only_fields = ['trip']

class ELDLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELDLog
        fields = '__all__'
        read_only_fields = ['trip']

class TripSerializer(serializers.ModelSerializer):
    driver = UserSerializer(read_only=True)
    eld_logs = ELDLogSerializer(many=True, read_only=True)
    route_stops = RouteStopSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['driver', 'start_time', 'end_time', 'total_distance', 'estimated_arrival']
    
    def create(self, validated_data):
       
        driver = self.context['request'].user
        trip = Trip.objects.create(driver=driver, **validated_data)
        return trip

class TripPlanningSerializer(serializers.Serializer):
    """Serializer for route planning input"""
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_hours = serializers.FloatField()