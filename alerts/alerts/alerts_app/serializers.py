from rest_framework import serializers

from . import models


class Alert(serializers.ModelSerializer):
    scheduled = serializers.ReadOnlyField()
    task_name = serializers.ReadOnlyField()

    class Meta:
        model = models.Alert
        exclude = ("task",)
