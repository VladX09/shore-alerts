import itertools
from unittest import mock

import arrow
import pytest
from insights_app.alerts_client import AlertItem
from insights_app.jobs.price_decrease_job import prepare_email_data, select_price_minmax


BASE_DT = arrow.Arrow(2022, 4, 6, tzinfo="UTC")


@pytest.fixture
def alerts_client_mock():
    id_counter = itertools.count()

    items = []
    alerts_client = mock.MagicMock()
    for email in ["aaa@example.com", "bbb@example.com", "ccc@example.com"]:
        alert_data = {
            "email": email,
            "query": "Text",
            "every": 10,
            "period": "minutes",
        }

        for item_id in ["item_1", "item_2", "item_3"]:
            for currency in ["USD", "RUB"]:
                for dt_shift in range(1, 4):
                    updated_at = BASE_DT.shift(hours=dt_shift)
                    item_data = {
                        "id": next(id_counter),
                        "item_id": item_id,
                        "title": "Text",
                        "web_url": "http://test.com",
                        "price": dt_shift * 100,
                        "currency": currency,
                        "alert": alert_data,
                        "updated_at": updated_at,
                    }
                    items.append(item_data)

    items = sorted(
        items,
        key=lambda item: (
            item["alert"]["email"],
            item["item_id"],
            item["currency"],
            item["updated_at"],
        ),
    )
    items = [AlertItem(**item) for item in items]
    alerts_client.get_alert_items.return_value = items
    return alerts_client


def test_select_price_minmax(alerts_client_mock):
    groups = select_price_minmax(BASE_DT.shift(days=-1), alerts_client_mock)

    for _, (earliest_item, latest_item) in groups:
        assert earliest_item.price == 100
        assert latest_item.price == 300


def test_prepare_email_data(alerts_client_mock):
    high_price_item = mock.MagicMock(
        price=100,
        title="High Price",
        web_url="http://whocares.com/high",
    )

    low_price_item = mock.MagicMock(
        price=98,
        title="Low Price",
        web_url="http://whocares.com/low",
    )

    groups = [
        (("aaa@example.com", "item_1", "EUR"), [high_price_item, low_price_item]),
        (("aaa@example.com", "item_1", "RUB"), [low_price_item, high_price_item]),
        (("aaa@example.com", "item_2", "EUR"), [low_price_item, high_price_item]),
        (("aaa@example.com", "item_2", "RUB"), [high_price_item, low_price_item]),
        (("bbb@example.com", "item_3", "RUB"), [high_price_item, low_price_item]),
    ]

    email_data = prepare_email_data(groups, 0.02)
    assert len(email_data.keys()) > 0

    mails = itertools.chain.from_iterable(email_data.values())
    for mail in mails:
        assert mail["old_price"] >= mail["new_price"]
