import uuid

from django.db import models


class Document(models.Model):
	class Status(models.TextChoices):
		DRAFT = 'draft', 'Draft'
		PUBLISHED = 'published', 'Published'
		ARCHIVED = 'archived', 'Archived'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=255)
	content = models.TextField()
	workspace = models.ForeignKey(
		'workspaces.Workspace',
		on_delete=models.CASCADE,
		related_name='documents',
	)
	created_by = models.ForeignKey(
		'users.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='documents',
	)
	status = models.CharField(
		max_length=20,
		choices=Status.choices,
		default=Status.DRAFT,
	)
	tags = models.ManyToManyField('tags.Tag', related_name='documents', blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self._was_adding = self._state.adding
		return super().save(*args, **kwargs)


class DocumentVersion(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	document = models.ForeignKey(
		Document,
		on_delete=models.CASCADE,
		related_name='versions',
	)
	content = models.TextField()
	version_number = models.PositiveIntegerField()
	saved_by = models.ForeignKey(
		'users.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='saved_document_versions',
	)
	saved_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['version_number']
		constraints = [
			models.UniqueConstraint(
				fields=['document', 'version_number'],
				name='unique_document_version_number',
			)
		]
