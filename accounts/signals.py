from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=User)
def store_plaintext_password(sender, instance, **kwargs):
    """
    Store plaintext password if password field is being updated.
    This allows admin to see the password when changing it.
    """
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            # Check if password has changed
            if old_user.password != instance.password and hasattr(instance, '_plaintext_password'):
                instance.plaintext_password = getattr(instance, '_plaintext_password', '')
        except User.DoesNotExist:
            pass

