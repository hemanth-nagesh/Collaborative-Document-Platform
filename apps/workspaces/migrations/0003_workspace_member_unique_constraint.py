from django.db import migrations, models


def ensure_unique_workspace_member(apps, schema_editor):
    WorkspaceMember = apps.get_model('workspaces', 'WorkspaceMember')

    constraint = models.UniqueConstraint(
        fields=('workspace', 'user'),
        name='unique_workspace_member',
    )

    try:
        schema_editor.add_constraint(WorkspaceMember, constraint)
    except Exception:
        # If it already exists (or cannot be added), ignore.
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('workspaces', '0002_sync_workspaces_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(ensure_unique_workspace_member, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='workspacemember',
                    name='unique_membership',
                ),
                migrations.AddConstraint(
                    model_name='workspacemember',
                    constraint=models.UniqueConstraint(
                        fields=('workspace', 'user'),
                        name='unique_workspace_member',
                    ),
                ),
            ],
        ),
    ]
