# Generated by Django 4.2.5 on 2023-09-09 03:38

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.UUIDField(default=uuid.uuid4)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('is_verified', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('address', models.CharField(default=None, max_length=512, null=True)),
                ('phone', models.CharField(max_length=20)),
                ('otp', models.IntegerField(default=True)),
                ('otp_expiration', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_dtm', models.DateTimeField(default=None)),
                ('modified_dtm', models.DateTimeField(default=None)),
            ],
        ),
    ]
