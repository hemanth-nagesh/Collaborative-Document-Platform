import uuid

from django.db import models


class AuditLog(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	actor = models.ForeignKey(
		'users.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='audit_logs',
	)
	action = models.CharField(max_length=50)
	model_name = models.CharField(max_length=100)
	object_id = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True)
