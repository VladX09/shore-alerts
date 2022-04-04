import typing as t

from rest_framework import serializers

from . import models


class Alert(serializers.ModelSerializer):
    scheduled = serializers.ReadOnlyField()
    task_name = serializers.ReadOnlyField()

    class Meta:
        model = models.Alert
        exclude = ("task",)


class AlertItem(serializers.ModelSerializer):
    alert = Alert()

    class Meta:
        model = models.AlertItem
        fields = "__all__"


class EbayImageSummarySchema(serializers.Serializer):
    imageUrl = serializers.CharField()


class EbayPriceSchema(serializers.Serializer):
    value = serializers.FloatField(required=False)
    currency = serializers.CharField(required=False)


class EbayItemSummarySchema(serializers.Serializer):
    itemId = serializers.CharField()
    title = serializers.CharField()
    price = EbayPriceSchema()
    itemWebUrl = serializers.URLField()


def parse_ebay_item(alert: models.Alert, ebay_item: t.Dict) -> models.AlertItem:
    schema = EbayItemSummarySchema(data=ebay_item)

    schema.is_valid(raise_exception=True)
    validated_data = schema.validated_data

    item = models.AlertItem(
        item_id=validated_data["itemId"],
        title=validated_data["title"],
        web_url=validated_data["itemWebUrl"],
        price=validated_data["price"].get("value"),
        currency=validated_data["price"].get("currency"),
    )

    item.alert = alert
    return item
