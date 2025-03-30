import os
from datetime import timedelta
from django.utils import timezone 
from rest_framework import permissions, status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from dotenv import load_dotenv
import googlemaps
from .models import Trip, ELDLog, RouteStop
from .serializers import TripSerializer, ELDLogSerializer, RouteStopSerializer, TripPlanningSerializer
load_dotenv()

class TripPlanningView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TripPlanningSerializer(data=request.data)
        if serializer.is_valid():
            gmaps = googlemaps.Client(key=os.getenv('GOOGLEMAP_API'))
            
            # Calculate route with pickup as waypoint
            directions = gmaps.directions(
                origin=serializer.validated_data['current_location'],
                destination=serializer.validated_data['dropoff_location'],
                waypoints=[serializer.validated_data['pickup_location']]
            )
            
            # Create Trip instance
            trip = Trip.objects.create(
                driver=request.user,
                current_location=serializer.validated_data['current_location'],
                pickup_location=serializer.validated_data['pickup_location'],
                dropoff_location=serializer.validated_data['dropoff_location'],
                current_cycle_hours=serializer.validated_data['current_cycle_hours'],
                status='PLANNED'
            )
            
            # Serializing the trip instance
            trip_serializer = TripSerializer(trip, context={'request': request})
            
            # Generate Route Stops and ELD Logs
            route_stops = self._generate_route_stops(directions, trip)
            eld_logs = self._generate_eld_logs(trip, serializer.validated_data['current_cycle_hours'])
            
            # Ensure all data is serialized
            return Response({
                'trip': trip_serializer.data,  # Dictionary from TripSerializer
                'route_coordinates': self._extract_route_coordinates(directions),
                'estimated_time': directions[0]['legs'][0]['duration']['text'] if directions else 'N/A',
                'route_stops': RouteStopSerializer(route_stops, many=True).data, 
                'eld_logs': ELDLogSerializer(eld_logs, many=True).data 
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _extract_route_coordinates(self, directions):
        if not directions or not directions[0]['legs']:
            return []
        return [
            (step['start_location']['lat'], step['start_location']['lng'])
            for step in directions[0]['legs'][0]['steps']
        ]
    
    def _generate_route_stops(self, directions, trip):
        route_stops = []
        if not directions or not directions[0]['legs']:
            return route_stops
        
        legs = directions[0]['legs']
        
        # Pickup Stop
        route_stops.append(RouteStop.objects.create(
            trip=trip,
            stop_type='PICKUP',
            location=trip.pickup_location,
            arrival_time=timezone.now(),
            duration=0.5
        ))
        
        # Rest Stops
        driving_time = sum(
            step['duration']['value'] for leg in legs 
            for step in leg['steps'] if step['travel_mode'] == 'DRIVING'
        ) / 3600
        rest_stops_count = int(driving_time // 4)
        for i in range(rest_stops_count):
            route_stops.append(RouteStop.objects.create(
                trip=trip,
                stop_type='REST',
                location='Rest Area',
                arrival_time=timezone.now(),
                duration=0.75
            ))
        
        # Dropoff Stop
        route_stops.append(RouteStop.objects.create(
            trip=trip,
            stop_type='DROPOFF',
            location=trip.dropoff_location,
            arrival_time=timezone.now(),
            duration=0.5
        ))
        
        return route_stops
    
    def _generate_eld_logs(self, trip, current_cycle_hours):
        eld_logs = []
        remaining_drive_hours = 11 - current_cycle_hours
        
        if remaining_drive_hours > 0:
            eld_logs.append(ELDLog.objects.create(
                trip=trip,
                log_type='DRIVING',
                start_time=timezone.now(),
                end_time=timezone.now() + timedelta(hours=remaining_drive_hours),
                duration_hours=remaining_drive_hours
            ))
        
        eld_logs.append(ELDLog.objects.create(
            trip=trip,
            log_type='OFF_DUTY',
            start_time=timezone.now() + timedelta(hours=remaining_drive_hours),
            end_time=timezone.now() + timedelta(hours=remaining_drive_hours + 10),
            duration_hours=10
        ))
        
        return eld_logs
    
    
    
class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their trips
        return Trip.objects.filter(driver=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete_trip(self, pk=None):
        """Mark a trip as completed"""
        trip = self.get_object()
        trip.status = 'COMPLETED'
        trip.end_time = timezone.now()
        trip.save()
        
        serializer = self.get_serializer(trip)
        return Response(serializer.data)