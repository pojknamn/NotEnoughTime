from django.db import models
from conf import FAILED, CREATED, PENDING, WORKING, DONE, CLOSED, RMTREE
# Create your models here.

class FoldersModel(models.Model):
    ident = models.CharField(max_length=40)
    path = models.CharField(max_length=500)


class TicketModel(models.Model):
    STATUSES = [
        (FAILED, 'FAILED'),
        (CREATED, 'CREATED'),
        (PENDING, "PENDING"),
        (WORKING, 'WORKING'),
        (DONE, 'DONE'),
        (CLOSED, 'CLOSED'),
        (RMTREE, 'REMOVE FOLDER')
    ]
    ticket_id = models.CharField(unique=True, max_length=40)
    user_id = models.IntegerField(default=0)
    working_directory = models.CharField(max_length=1000)
    serial = models.BooleanField(default=1)
    recursive = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUSES, default=CREATED)
    speed = models.FloatField(max_length=10, default=2.0)
    subtitles = models.BooleanField(default=False)
    external_audio = models.CharField(max_length=1000)
    folders_json = models.JSONField(default=dict())
    items = models.JSONField(default={"items": list()})
    errors = models.JSONField(default={"errors": list()})
