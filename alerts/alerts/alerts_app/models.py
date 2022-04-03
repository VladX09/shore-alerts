import json
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Alert(BaseModel):
    email = models.EmailField()
    query = models.TextField()
    every = models.IntegerField(
        null=False,
        validators=[MinValueValidator(1)],
    )
    period = models.CharField(
        max_length=24,
        choices=IntervalSchedule.PERIOD_CHOICES,
    )
    task = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alert",
    )

    @property
    def scheduled(self) -> bool:
        return self.task is not None

    def __str__(self) -> str:
        return (
            f"Alert({self.id}, {self.email}, {self.query}, {self.every}, {self.period})"
        )


@receiver(pre_save, sender=Alert)
def alert_pre_save(sender, instance, *args, **kwargs):
    interval, _ = IntervalSchedule.objects.get_or_create(
        every=instance.every,
        period=instance.period,
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

    instance.task = task


@receiver(post_delete, sender=Alert)
def alert_post_delete(sender, instance, *args, **kwargs):
    """Delete task on alert delete."""
    if instance.task:
        instance.task.delete()
