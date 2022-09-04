from django.db import models

# Create your models here.


class PendingModel(models.Model):
    folder_path = models.CharField(max_length=500)
    rendered = models.BooleanField(default=False)
    ident = models.CharField(max_length=40)
    status = models.CharField(max_length=40, default='DOWNLOADED')
    has_content = models.BooleanField(default=False)
    is_file = models.BooleanField(default=False)
