from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import Account
from django.utils import timezone

@receiver(post_save, sender=Account)
def handle_account_activity(sender, instance, **kwargs):
    # Update last activity on any account change
    instance.last_activity = timezone.now()
    instance.save()