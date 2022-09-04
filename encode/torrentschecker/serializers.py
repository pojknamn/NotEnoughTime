from rest_framework import serializers
from .models import PendingModel


class TorrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingModel
        fields = ('folder_path', 'rendered', 'status',)
