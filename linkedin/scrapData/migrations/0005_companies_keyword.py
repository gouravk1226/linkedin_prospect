# Generated by Django 3.2.6 on 2021-09-07 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapData', '0004_alter_usersdata_valid_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='companies',
            name='keyword',
            field=models.CharField(default='NA', max_length=255),
        ),
    ]
