from alerts.celery import celery_app
from alerts.ebay import ebay_client
from alerts.settings import EMAIL_HOST_USER
from celery.utils.log import get_task_logger
from django_celery_beat.models import PeriodicTask
from templated_email import send_templated_mail

from . import serializers


logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def compose_and_send_alert(self, task_id: str):
    task_obj: PeriodicTask = PeriodicTask.objects.get(name=task_id)
    params = {
        "q": task_obj.alert.query,
        "sort": "price",
        "limit": 20,
    }
    location_header = ebay_client.generate_enduserctx(
        task_obj.alert.country,
        task_obj.alert.zip_code,
    )
    response = ebay_client.search_items(params=params, headers=location_header)

    items = [
        serializers.parse_ebay_item(task_obj.alert, item_src)
        for item_src in response.get("itemSummaries", [])
    ]
    items = sorted(items, key=lambda i: i.price)

    send_templated_mail(
        template_name="alert_mail",
        from_email=EMAIL_HOST_USER,
        recipient_list=[task_obj.alert.email],
        context={
            "alert_query": task_obj.alert.query,
            "ebay_items": [serializers.AlertItem(item).data for item in items],
        },
    )

    for item in items:
        item.save()
