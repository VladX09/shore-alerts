from alerts.celery import celery_app
from alerts.ebay import ebay_client
from alerts.settings import EMAIL_HOST_USER
from celery.utils.log import get_task_logger
from django_celery_beat.models import PeriodicTask
from templated_email import send_templated_mail

from common_lib.dataclasses.ebay import EbayItem


logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def compose_and_send_alert(self, task_id: str):
    task_obj: PeriodicTask = PeriodicTask.objects.get(name=task_id)
    response = ebay_client.search_items(q=task_obj.alert.query, sort="price", limit=20)
    items = [EbayItem.parse(item_src) for item_src in response.get("itemSummaries", [])]

    if not items:
        logger.info("Skip empty items list for alert: %s", task_obj.alert)
        return

    send_templated_mail(
        template_name="alert_mail",
        from_email=EMAIL_HOST_USER,
        recipient_list=[task_obj.alert.email],
        context={
            "ebay_items": [item.asdict() for item in items],
        },
    )
