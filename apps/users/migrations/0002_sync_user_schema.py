from django.db import migrations


def _existing_columns(schema_editor, table_name):
    connection = schema_editor.connection
    if table_name not in connection.introspection.table_names():
        return set()

    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
    return {col.name for col in description}


def _add_field_if_missing(model, field_name, schema_editor):
    table_name = model._meta.db_table
    existing = _existing_columns(schema_editor, table_name)

    field = model._meta.get_field(field_name)
    if field.column in existing:
        return

    schema_editor.add_field(model, field)


def sync_users_user_table(apps, schema_editor):
    User = apps.get_model('users', 'User')

    for field_name in [
        'first_name',
        'last_name',
        'email',
        'phone',
        'created_at',
    ]:
        _add_field_if_missing(User, field_name, schema_editor)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_users_user_table, migrations.RunPython.noop),
    ]
