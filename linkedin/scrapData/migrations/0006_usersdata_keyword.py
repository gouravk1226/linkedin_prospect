# Generated by Django 3.2.6 on 2021-09-17 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapData', '0005_companies_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersdata',
            name='keyword',
            field=models.CharField(default='NA', max_length=255),
        ),
    ]