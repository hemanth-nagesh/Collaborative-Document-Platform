from django.db import migrations


def _add_field_if_missing(model, field_name, schema_editor):
    # Introspect live DB columns for this table.
    table_name = model._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            [table_name],
        )
        existing = {row[0] for row in cursor.fetchall()}

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
