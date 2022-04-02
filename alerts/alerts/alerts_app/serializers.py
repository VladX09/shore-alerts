from rest_framework import serializers

from . import models


class Alert(serializers.ModelSerializer):
    class Meta:
        model = models.Alert
        fields = ["id", "email", "query", "period"]