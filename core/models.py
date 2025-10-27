from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class Skill(models.Model):
    """Skills that technicians can have"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)


class GoogleMapsConfig(models.Model):
    """Singleton model for Google Maps configuration"""
    api_key = models.CharField(max_length=500, help_text="Google Maps API Key")
    avg_speed_kph = models.IntegerField(default=40, help_text="Average speed in km/h")
    late_penalty_per_min = models.IntegerField(default=500, help_text="Penalty per minute of lateness")
    drop_penalty_per_job = models.IntegerField(default=100000, help_text="Penalty per dropped job")
    return_to_depot = models.BooleanField(default=True, help_text="Return to depot at end of day")
    time_limit_seconds = models.IntegerField(default=30, help_text="OR-Tools solver time limit")
    
    class Meta:
        verbose_name = "Google Maps Configuration"
        verbose_name_plural = "Google Maps Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion
        pass
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Google Maps Configuration"


class Technician(models.Model):
    """Technician profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    depot_address = models.CharField(max_length=500, help_text="Depot address")
    depot_lat = models.FloatField(null=True, blank=True, help_text="Depot latitude")
    depot_lon = models.FloatField(null=True, blank=True, help_text="Depot longitude")
    capacity_minutes = models.IntegerField(default=480, help_text="Daily capacity in minutes")
    shift_start = models.TimeField(help_text="Shift start time")
    shift_end = models.TimeField(help_text="Shift end time")
    color_hex = models.CharField(max_length=7, default='#4285F4', help_text="Route color (hex)")
    skills = models.ManyToManyField(Skill, related_name='technicians')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.depot_address}"
    
    def clean(self):
        # Validate color_hex format
        if self.color_hex:
            hex_pattern = re.compile(r'^#([0-9a-fA-F]{6})$')
            if not hex_pattern.match(self.color_hex):
                raise ValidationError({'color_hex': 'Invalid hex color format. Use format #RRGGBB'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ServiceRequest(models.Model):
    """Customer service request"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    service_minutes = models.IntegerField(help_text="Service duration in minutes")
    window_start = models.DateTimeField(help_text="Earliest acceptable arrival time")
    window_end = models.DateTimeField(help_text="Latest acceptable arrival time")
    required_skills = models.ManyToManyField(Skill, related_name='service_requests')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.customer.username}"
    
    def has_active_assignment(self):
        return self.assignments.filter(status__in=['assigned', 'in_progress']).exists()


class Assignment(models.Model):
    """Job assignment to technician"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='assignments')
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    assigned_date = models.DateField()
    sequence_order = models.IntegerField(help_text="Order in technician's route")
    planned_start = models.DateTimeField(help_text="Planned arrival time")
    planned_finish = models.DateTimeField(help_text="Planned completion time")
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_finish = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    travel_time_minutes = models.FloatField(default=0, help_text="Travel time from previous location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['assigned_date', 'technician', 'sequence_order']
        unique_together = ['service_request', 'assigned_date']
    
    def __str__(self):
        return f"{self.technician.user.username} - {self.service_request.name} ({self.assigned_date})"
