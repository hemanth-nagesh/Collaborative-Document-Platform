import uuid

from django.db import models

role_choices = [
	('admin', 'Admin'),
	('editor', 'Editor'),
	('viewer', 'Viewer')
]
class Workspace(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_workspaces')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

class WorkspaceMember(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
	user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='workspace_memberships')
	role = models.CharField(max_length=10, choices=role_choices, default='viewer')
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['workspace', 'user'], name='unique_workspace_member')
		]