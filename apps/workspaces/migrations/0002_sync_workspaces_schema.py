from django.db import migrations


def _existing_columns(schema_editor, table_name: str):
    connection = schema_editor.connection
    if table_name not in connection.introspection.table_names():
        return set()

    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
    return {col.name for col in description}


def _add_field_if_missing(model, field_name: str, schema_editor):
    existing = _existing_columns(schema_editor, model._meta.db_table)
    field = model._meta.get_field(field_name)
    if field.column in existing:
        return
    schema_editor.add_field(model, field)


def _add_constraint_if_missing(model, constraint_name: str, schema_editor):
    # Best-effort: try add_constraint and ignore if already exists.
    constraint = next(
        (c for c in model._meta.constraints if getattr(c, 'name', None) == constraint_name),
        None,
    )
    if constraint is None:
        return

    try:
        schema_editor.add_constraint(model, constraint)
    except Exception:
        pass


def sync_workspaces_tables(apps, schema_editor):
    Workspace = apps.get_model('workspaces', 'Workspace')
    WorkspaceMember = apps.get_model('workspaces', 'WorkspaceMember')

    # Workspace fields
    for field_name in ['name', 'is_active', 'created_at', 'owner']:
        _add_field_if_missing(Workspace, field_name, schema_editor)

    # WorkspaceMember fields
    for field_name in ['role', 'joined_at', 'user', 'workspace']:
        _add_field_if_missing(WorkspaceMember, field_name, schema_editor)

    # Unique constraint (workspace, user)
    _add_constraint_if_missing(WorkspaceMember, 'unique_workspace_member', schema_editor)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_workspaces_tables, migrations.RunPython.noop),
    ]
