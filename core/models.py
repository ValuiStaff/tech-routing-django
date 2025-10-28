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
    required_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_requests', help_text="Required skill for this service (one skill per request)")
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
    
    def get_skills_match_info(self):
        """Get info about required skill vs technician's skills"""
        if not self.technician or not self.service_request:
            return None
        
        # Service request now has single required skill
        required_skill_name = self.service_request.required_skill.name if self.service_request.required_skill else None
        required_skills = {required_skill_name} if required_skill_name else set()
        
        tech_skills = set(self.technician.skills.values_list('name', flat=True))
        
        matched = required_skills & tech_skills
        missing = required_skills - tech_skills
        extra = tech_skills - required_skills
        
        return {
            'required': sorted(required_skills),
            'tech_has': sorted(tech_skills),
            'matched': sorted(matched),
            'missing': sorted(missing),
            'extra': sorted(extra),
            'is_match': len(missing) == 0,
        }
    
    def get_time_window_info(self):
        """Get info about whether technician is available within customer's time window"""
        if not self.technician:
            return None
        
        from django.utils import timezone
        from datetime import datetime
        
        # Get customer's requested time window
        customer_start = self.service_request.window_start
        customer_end = self.service_request.window_end
        
        # Get technician's shift for the assigned date
        shift_start = datetime.combine(self.assigned_date, self.technician.shift_start)
        shift_end = datetime.combine(self.assigned_date, self.technician.shift_end)
        shift_start = timezone.make_aware(shift_start)
        shift_end = timezone.make_aware(shift_end)
        
        # Check if customer window is within technician shift
        is_within_window = (shift_start <= customer_start <= shift_end) and (shift_start <= customer_end <= shift_end)
        
        return {
            'customer_window_start': customer_start,
            'customer_window_end': customer_end,
            'tech_shift_start': shift_start,
            'tech_shift_end': shift_end,
            'is_within_window': is_within_window,
        }
