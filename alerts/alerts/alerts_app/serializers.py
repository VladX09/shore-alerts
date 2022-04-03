import json

from django.db import transaction
from django_celery_beat import models as beat_models
from rest_framework import serializers

from . import models


class Alert(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    query = serializers.CharField()
    every = serializers.IntegerField(min_value=1)
    period = serializers.ChoiceField(
        choices=beat_models.IntervalSchedule.PERIOD_CHOICES
    )

    def create(self, validated_data):
        with transaction.atomic():
            interval, _ = beat_models.IntervalSchedule.objects.get_or_create(
                every=validated_data["every"],
                period=validated_data["period"],
            )
            task = beat_models.PeriodicTask.objects.create(
                interval=interval,
                name="Send alert",
                task="alerts_app.tasks.compose_and_send_alert",
            )
            alert = models.Alert.objects.create(
                email=validated_data["email"],
                query=validated_data["query"],
                task=task,
            )
            alert.task.kwargs = json.dumps(
                {
                    "alert_id": alert.id,
                }
            )
            alert.task.save()
            return alert

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = {}
        ret["id"] = instance.id
        ret["email"] = instance.email
        ret["query"] = instance.query
        ret["every"] = instance.task.interval.every
        ret["period"] = instance.task.interval.period
        return ret
