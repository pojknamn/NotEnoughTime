# Generated by Django 4.0.1 on 2022-09-04 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PendingModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_path', models.CharField(max_length=500)),
                ('rendered', models.BooleanField(default=False)),
                ('ident', models.CharField(max_length=40)),
                ('status', models.CharField(default='DOWNLOADED', max_length=40)),
                ('has_content', models.BooleanField(default=False)),
                ('is_file', models.BooleanField(default=False)),
            ],
        ),
    ]
