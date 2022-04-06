from alerts_app import models
from django.test import Client, TestCase
from django_celery_beat import models as beat_models


class Suite(TestCase):
    def test_alert_operations(self):
        c = Client()
        response = c.post(
            "/api/v1/alerts/",
            {
                "email": "test@example.com",
                "query": "Drone",
                "every": 10,
                "period": "seconds",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        alerts = models.Alert.objects.all()
        self.assertEqual(len(alerts), 1)

        alert: models.Alert = alerts[0]
        alert_id = alert.id
        self.assertIsNotNone(alert.task)

        task_id = alert.task.id
        self.assertEqual(alert.task.interval.every, 10)
        self.assertEqual(alert.task.interval.period, "seconds")

        response = c.patch(
            f"/api/v1/alerts/{alert.id}/",
            {
                "every": 20,
                "period": "minutes",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        alert.refresh_from_db()
        self.assertIsNotNone(alert.task)
        self.assertEqual(alert.task.interval.every, 20)
        self.assertEqual(alert.task.interval.period, "minutes")
        self.assertEqual(alert.task.id, task_id)

        response = c.delete(
            f"/api/v1/alerts/{alert.id}/",
        )
        self.assertEqual(response.status_code, 204)

        self.assertIsNone(models.Alert.objects.filter(pk=alert_id).first())
        self.assertIsNone(beat_models.PeriodicTask.objects.filter(pk=task_id).first())
