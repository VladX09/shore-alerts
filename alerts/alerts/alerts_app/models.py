from django.db import models
from django_celery_beat.models import PeriodicTask


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Alert(BaseModel):
    email = models.EmailField()
    query = models.TextField()
    task = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Alert({self.id}, {self.email}, {self.query}, {self.task.interval})"
