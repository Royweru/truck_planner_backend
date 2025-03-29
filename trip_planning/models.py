from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Trip(models.Model):
    """Model to store trip details"""
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    current_cycle_hours = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(14)  # Max driving hours per day
        ]
    )
    
    total_distance = models.FloatField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')

class ELDLog(models.Model):
    """Electronic Logging Device (ELD) Log Entry"""
    trip = models.ForeignKey(Trip, related_name='eld_logs', on_delete=models.CASCADE)
    
    LOG_TYPE_CHOICES = [
        ('DRIVING', 'Driving'),
        ('ON_DUTY', 'On Duty'),
        ('OFF_DUTY', 'Off Duty'),
        ('SLEEPER', 'Sleeper Berth')
    ]
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.FloatField()
    location = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.trip.driver.username} - {self.log_type} - {self.start_time}"

class RouteStop(models.Model):
    """Stops along a trip route"""
    trip = models.ForeignKey(Trip, related_name='route_stops', on_delete=models.CASCADE)
    
    STOP_TYPE_CHOICES = [
        ('PICKUP', 'Pickup'),
        ('DROPOFF', 'Dropoff'),
        ('REST', 'Rest Stop'),
        ('FUEL', 'Fuel Stop')
    ]
    
    stop_type = models.CharField(max_length=20, choices=STOP_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(help_text="Duration of stop in hours")
