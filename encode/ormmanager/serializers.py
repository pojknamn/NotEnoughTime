from rest_framework import serializers

from .models import TicketModel


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketModel
        fields = ('ticket_id', 'errors', 'status', 'working_directory')
