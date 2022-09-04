from rest_framework import generics, permissions
from .serializers import TorrentSerializer
from .models import PendingModel

class TorrentsAPIView(generics.ListAPIView):
    queryset = PendingModel.objects.all()
    serializer_class = TorrentSerializer
    permission_classes = (permissions.IsAuthenticated, )


