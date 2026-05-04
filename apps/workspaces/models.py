import uuid

from django.db import models


class Workspace(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class WorkspaceMember(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
