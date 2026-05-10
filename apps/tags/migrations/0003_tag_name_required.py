from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tags', '0002_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
