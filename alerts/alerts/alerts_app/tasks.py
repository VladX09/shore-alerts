import typing as t

from alerts.celery import celery_app
from alerts.ebay import ebay_client
from alerts.settings import SENDER_EMAIL
from celery.utils.log import get_task_logger
from django_celery_beat.models import PeriodicTask
from templated_email import send_templated_mail

from . import models, serializers


logger = get_task_logger(__name__)


def get_previous_prices(alert_id: int, item_ids: t.Set[str]):
    """Get last item price for each item in given alert."""
    query = (
        models.AlertItem.objects.filter(
            alert__id__exact=alert_id,
            item_id__in=item_ids,
        )
        .order_by("item_id", "-updated_at")
        .distinct("item_id")
    )

    return {item.item_id: item.price for item in query}


@celery_app.task(bind=True)
def compose_and_send_alert(self, task_id: str):
    task_obj: PeriodicTask = PeriodicTask.objects.get(name=task_id)

    response = ebay_client.search_items(q=task_obj.alert.query, sort="price", limit=20)
    items = [
        serializers.parse_ebay_item(task_obj.alert, item_src)
        for item_src in response.get("itemSummaries", [])
    ]

    # Send only new items or items with new price
    prev_prices = get_previous_prices(
        alert_id=task_obj.alert.id,
        item_ids=set(i.item_id for i in items),
    )

    items_filtered = []
    for item in sorted(items, key=lambda i: i.price):
        if item.item_id not in prev_prices or item.price != prev_prices[item.item_id]:
            items_filtered.append(item)

    if items_filtered:
        logger.debug("Send %s changed items", len(items_filtered))
        send_templated_mail(
            template_name="alert_mail",
            from_email=SENDER_EMAIL,
            recipient_list=[task_obj.alert.email],
            context={
                "alert_query": task_obj.alert.query,
                "ebay_items": [
                    serializers.AlertItem(item).data for item in items_filtered
                ],
            },
        )

    else:
        logger.debug("Skip emailing")

    # Save all items for future analysis
    for item in items:
        item.save()
