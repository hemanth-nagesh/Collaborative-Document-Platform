from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.audit.models import AuditLog

from .models import Document


@receiver(post_save, sender=Document)
def create_document_audit_log(sender, instance, **kwargs):
    was_adding = getattr(instance, '_was_adding', False)
    action = 'created' if was_adding else 'updated'
    AuditLog.objects.create(
        actor=instance.created_by,
        action=action,
        model_name='Document',
        object_id=str(instance.id),
    )
