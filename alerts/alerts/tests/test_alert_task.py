from unittest import mock

import arrow
from alerts_app import models, tasks
from django.test import TestCase


class UnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alert = models.Alert.objects.create(
            email="a@domain.com",
            query="Drone",
            every=10,
            period="minutes",
        )
        cls.items = []

        for day_shift, item_id, price in [
            (-1, "item_1", 100),
            (-2, "item_1", 150),
            (-1, "item_2", 200),
            (0, "item_2", 150),
        ]:
            date = arrow.now().shift(days=day_shift)
            with mock.patch(
                "django.utils.timezone.now", mock.Mock(return_value=date.datetime)
            ):
                cls.items.append(
                    models.AlertItem.objects.create(
                        item_id=item_id,
                        title="Title",
                        web_url="http://url.com",
                        price=price,
                        currency="RUB",
                        alert=cls.alert,
                    )
                )

        cls.new_items = [
            models.AlertItem(
                item_id="item_1",
                title="Title",
                web_url="http://url.com",
                price=100,
                currency="RUB",
                alert=cls.alert,
            ),  # NOT CHANGED
            models.AlertItem(
                item_id="item_2",
                title="Title",
                web_url="http://url.com",
                price=300,
                currency="RUB",
                alert=cls.alert,
            ),  # CHANGED
            models.AlertItem(
                item_id="item_3",
                title="Title",
                web_url="http://url.com",
                price=300,
                currency="RUB",
                alert=cls.alert,
            ),  # NEW
        ]

    def test_get_previous_prices(self):
        prev_prices = tasks.get_previous_prices(
            alert_id=self.alert.id,
            item_ids=set(("item_1", "item_2")),
        )
        self.assertEqual(prev_prices, {"item_1": 100, "item_2": 150})

    def test_filter_items(self):
        filtered_items = tasks.filter_items(
            alert_id=self.alert.id,
            items=self.new_items,
        )
        self.assertEqual(len(filtered_items), 2)
        self.assertEqual(filtered_items, self.new_items[1:])
