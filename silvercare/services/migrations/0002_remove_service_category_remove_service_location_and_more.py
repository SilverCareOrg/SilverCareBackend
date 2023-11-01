# Generated by Django 4.1.7 on 2023-10-30 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='category',
        ),
        migrations.RemoveField(
            model_name='service',
            name='location',
        ),
        migrations.RemoveField(
            model_name='service',
            name='price',
        ),
        migrations.RemoveField(
            model_name='service',
            name='rating',
        ),
        migrations.AddField(
            model_name='service',
            name='details',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='has_more_options',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ServiceOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField(default=0)),
                ('duration', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('map_location', models.CharField(max_length=100)),
                ('rating', models.FloatField(default=0)),
                ('number_ratings', models.IntegerField(default=0)),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.service')),
            ],
        ),
    ]
