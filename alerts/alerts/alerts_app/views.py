import json
import uuid
from logging import getLogger

from django.db import transaction
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import viewsets

from . import models, serializers


logger = getLogger(__name__)


class AlertItemViewSet(viewsets.ModelViewSet):
    queryset = models.AlertItem.objects.all()
    serializer_class = serializers.AlertItem


class AlertViewSet(viewsets.ModelViewSet):
    queryset = models.Alert.objects.all()
    serializer_class = serializers.Alert

    def perform_create(self, serializer):
        with transaction.atomic():
            data = serializer.validated_data

            interval, _ = IntervalSchedule.objects.get_or_create(
                every=data["every"],
                period=data["period"],
            )

            task_id = str(uuid.uuid4())

            task = PeriodicTask.objects.create(
                interval=interval,
                name=task_id,
                task="alerts_app.tasks.compose_and_send_alert",
                kwargs=json.dumps(
                    {
                        "task_id": task_id,
                    }
                ),
            )

            logger.debug("Adding task %s", task)
            serializer.save(task=task)

    def perform_update(self, serializer):
        with transaction.atomic():
            instance = serializer.save()

            interval, _ = IntervalSchedule.objects.get_or_create(
                every=instance.every,
                period=instance.period,
            )

            logger.debug("Updating task %s", instance.task)

            instance.task.interval = interval
            instance.task.save()

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()

        logger.debug("Removing task %s", instance.task)
        if task:
            task.delete()
