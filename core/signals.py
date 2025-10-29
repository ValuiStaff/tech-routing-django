from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Assignment, ServiceRequest


@receiver(post_save, sender=Assignment)
def update_service_request_status(sender, instance, created, **kwargs):
    """Update service request status when assignment is created or updated"""
    if instance.technician and instance.status in ['assigned', 'in_progress']:
        if instance.service_request.status != 'assigned':
            instance.service_request.status = 'assigned'
            instance.service_request.save()


@receiver(post_delete, sender=Assignment)
def reset_service_request_status(sender, instance, **kwargs):
    """Reset service request to pending when all assignments are deleted"""
    service_request = instance.service_request
    
    # Check if there are any remaining active assignments for this service request
    # (instance is already deleted, so we don't need to exclude it)
    remaining_active = Assignment.objects.filter(
        service_request=service_request,
        status__in=['assigned', 'in_progress'],
        technician__isnull=False
    ).exists()
    
    # Check if there are any remaining assignments at all (completed, cancelled, etc.)
    remaining_any = Assignment.objects.filter(
        service_request=service_request
    ).exists()
    
    # If no active assignments remaining, reset status
    if not remaining_active:
        # If all assignments are deleted, set to pending
        if not remaining_any:
            if service_request.status in ['assigned', 'in_progress']:
                service_request.status = 'pending'
                service_request.save()
        # If there are completed/cancelled assignments but no active ones
        # Keep status as is (might be completed or cancelled)

