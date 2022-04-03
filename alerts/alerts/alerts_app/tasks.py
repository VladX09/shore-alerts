from datetime import timedelta

from alerts.celery import celery_app
from alerts.ebay import ebay_client
from celery.utils.log import get_task_logger
from django.core.mail import send_mail

from common_lib.dataclasses.ebay import EbayItem

from . import models


logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def compose_and_send_alert(self, alert_id: int):
    alert_obj: models.Alert = models.Alert.objects.get(id=alert_id)
    response = ebay_client.search_items(q=alert_obj.query, sort="price", limit=20)
    items = [EbayItem.parse(item_src) for item_src in response["itemSummaries"]]
    logger.info("Got items: %s", items)
