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
    # Check if there are any remaining active assignments
    remaining = Assignment.objects.filter(
        service_request=instance.service_request,
        status__in=['assigned', 'in_progress'],
        technician__isnull=False
    ).exclude(id=instance.id).exists()
    
    if not remaining and instance.service_request.status == 'assigned':
        instance.service_request.status = 'pending'
        instance.service_request.save()

