# Generated by Django 4.0.1 on 2022-09-04 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FoldersModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ident', models.CharField(max_length=40)),
                ('path', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='TicketModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(max_length=40, unique=True)),
                ('user_id', models.IntegerField(default=0)),
                ('working_directory', models.CharField(max_length=1000)),
                ('serial', models.BooleanField(default=1)),
                ('recursive', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('F', 'FAILED'), ('C', 'CREATED'), ('P', 'PENDING'), ('W', 'WORKING'), ('D', 'DONE'), ('X', 'CLOSED'), ('R', 'REMOVE FOLDER')], default='C', max_length=1)),
                ('speed', models.FloatField(default=2.0, max_length=10)),
                ('subtitles', models.BooleanField(default=False)),
                ('external_audio', models.CharField(max_length=1000)),
                ('folders_json', models.JSONField(default={})),
                ('items', models.JSONField(default={'items': []})),
                ('errors', models.JSONField(default={'errors': []})),
            ],
        ),
    ]
