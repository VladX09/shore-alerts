from rest_framework import serializers

from . import models


class Alert(serializers.ModelSerializer):
    class Meta:
        model = models.Alert
        fields = ["id", "email", "query", "interval"]


class IntervalSchedule(serializers.ModelSerializer):
    class Meta:
        model = models.IntervalSchedule
        fields = ["id", "every", "period"]
