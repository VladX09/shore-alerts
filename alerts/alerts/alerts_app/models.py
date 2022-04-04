import typing as t

from django.core.validators import MinValueValidator
from django.db import models
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

    @property
    def task_name(self) -> t.Optional[str]:
        return self.task.name if self.task is not None else None

    def __str__(self) -> str:
        return (
            f"Alert({self.id}, {self.email}, {self.query}, {self.every}, {self.period})"
        )


class AlertItem(BaseModel):
    item_id = models.CharField(max_length=255)
    title = models.TextField()
    web_url = models.URLField()
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=8, null=True, blank=True)

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="items")

    def __str__(self) -> str:
        return f"AlertItem({self.item_id}, {self.title[:10]}...)"
