from rest_framework import viewsets

from . import models, serializers


class DungeonLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.DungeonLog.objects.all()
    serializer_class = serializers.DungeonLogSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['private'] = True
        return context