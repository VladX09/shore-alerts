import typing as t

import pydantic
import requests


class Alert(pydantic.BaseModel):
    email: str
    query: str
    every: int
    period: str


class AlertItem(pydantic.BaseModel):
    id: int
    item_id: str
    title: str
    web_url: str
    price: t.Optional[float]
    currency: t.Optional[str]
    alert: Alert


class AlertsClient:
    def __init__(self, url: str) -> None:
        self.url = url

    @property
    def alert_items_url(self) -> str:
        return f"{self.url}/api/v1/items"

    def get_alert_items(self, **params) -> t.List[AlertItem]:
        response = requests.get(url=self.alert_items_url, params=params)
        response.raise_for_status()

        return [AlertItem(**item) for item in response.json()]
