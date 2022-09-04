from rest_framework import generics
from .models import TicketModel
from .serializers import TicketSerializer


class TicketsAPIView(generics.ListAPIView):
        queryset = TicketModel.objects.all()
        serializer_class = TicketSerializer