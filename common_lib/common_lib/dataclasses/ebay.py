import typing as t
from dataclasses import asdict, dataclass

from rest_framework import serializers


class EbayImageSummarySchema(serializers.Serializer):
    imageUrl = serializers.CharField()


class EbayPriceSchema(serializers.Serializer):
    value = serializers.FloatField(required=False)
    currency = serializers.CharField(required=False)


class EbayItemSummarySchema(serializers.Serializer):
    title = serializers.CharField()
    image = EbayImageSummarySchema()
    itemHref = serializers.URLField()
    price = EbayPriceSchema()


@dataclass
class EbayItem:
    title: str
    href: str
    image_url: str
    price: t.Optional[str]
    currency: t.Optional[str]

    @classmethod
    def parse(cls, data: t.Dict[str, t.Any]):
        schema = EbayItemSummarySchema(data=data)

        schema.is_valid(raise_exception=True)
        validated_data = schema.validated_data

        return cls(
            title=validated_data["title"],
            href=validated_data["itemHref"],
            image_url=validated_data["image"]["imageUrl"],
            price=validated_data["price"].get("value"),
            currency=validated_data["price"].get("currency"),
        )

    def asdict(self):
        return asdict(self)
