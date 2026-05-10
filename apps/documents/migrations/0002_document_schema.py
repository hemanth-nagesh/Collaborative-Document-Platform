from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_sync_user_schema'),
        ('workspaces', '0003_workspace_member_unique_constraint'),
        ('tags', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='documents',
                to='users.user',
            ),
        ),
        migrations.AddField(
            model_name='document',
            name='status',
            field=models.CharField(
                choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')],
                default='draft',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='document',
            name='title',
            field=models.CharField(default='Untitled', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='document',
            name='workspace',
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='workspaces.workspace',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='documents', to='tags.tag'),
        ),
        migrations.AddField(
            model_name='documentversion',
            name='content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documentversion',
            name='document',
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='versions',
                to='documents.document',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documentversion',
            name='saved_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='documentversion',
            name='saved_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='saved_document_versions',
                to='users.user',
            ),
        ),
        migrations.AddField(
            model_name='documentversion',
            name='version_number',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='documentversion',
            constraint=models.UniqueConstraint(fields=('document', 'version_number'), name='unique_document_version_number'),
        ),
    ]
