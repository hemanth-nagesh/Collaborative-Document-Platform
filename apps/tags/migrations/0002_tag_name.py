from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
