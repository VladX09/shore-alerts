from rest_framework import viewsets

from . import models, serializers


class AlertViewSet(viewsets.ModelViewSet):
    queryset = models.Alert.objects.all()
    serializer_class = serializers.Alert
