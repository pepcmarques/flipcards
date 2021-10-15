# Generated by Django 3.2.8 on 2021-10-15 16:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cards', '0003_auto_20211015_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardtopic',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='card',
            unique_together={('topic', 'front', 'back')},
        ),
        migrations.AlterUniqueTogether(
            name='cardcollection',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='cardtopic',
            unique_together={('collection', 'name')},
        ),
    ]