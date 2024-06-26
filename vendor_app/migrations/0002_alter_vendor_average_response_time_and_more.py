# Generated by Django 5.0.3 on 2024-04-30 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='average_response_time',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='fulfillment_rate',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='on_time_delivery_rate',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='quality_rating_avg',
            field=models.FloatField(),
        ),
    ]
