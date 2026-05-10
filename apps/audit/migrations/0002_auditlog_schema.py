from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_sync_user_schema'),
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='action',
            field=models.CharField(default='created', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auditlog',
            name='actor',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='audit_logs',
                to='users.user',
            ),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='model_name',
            field=models.CharField(default='Document', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auditlog',
            name='object_id',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auditlog',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True),
            preserve_default=False,
        ),
    ]
