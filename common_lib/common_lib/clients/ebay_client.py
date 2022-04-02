import base64
import typing as t

import requests


B64_ENCODING = "utf-8"
AUTH_SCOPES = ["https://api.ebay.com/oauth/api_scope"]


class EbayClientError(Exception):
    pass


class EbayClientAuthError(Exception):
    pass


def encode_creds(app_id: str, cert_id: str) -> str:
    creds_str = f"{app_id}:{cert_id}"
    return base64.b64encode(creds_str.encode(B64_ENCODING)).decode(B64_ENCODING)


class EbayClient:
    def __init__(self, app_id: str, cert_id: str, auth_url: str, api_url: str) -> None:
        self._creds = encode_creds(app_id=app_id, cert_id=cert_id)
        self._auth_url = auth_url.rstrip("/")
        self._api_url = api_url.rstrip("/")

    # TODO: add readme note about token cache
    def get_app_access_token(self) -> str:
        headers = {
            "Authorization": f"Basic {self._creds}",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": " ".join(AUTH_SCOPES),
        }
        response = requests.post(url=self._auth_url, headers=headers, data=data)

        if response.status_code == requests.codes.ok:
            return response.json()["access_token"]

        raise EbayClientAuthError(
            f"Got auth response [{response.status_code}]: {response.text}"
        )

    def get_app_auth_header(self) -> t.Dict[str, str]:
        access_token = self.get_app_access_token()
        return {"Authorization": f"Bearer {access_token}"}

    @property
    def item_summary_search_url(self) -> str:
        return f"{self._api_url}/item_summary/search"

    def search_items(self, **params: str) -> t.Dict[str, t.Any]:
        auth_header = self.get_app_auth_header()
        response = requests.get(
            url=self.item_summary_search_url,
            headers=auth_header,
            params=params,
        )

        response.raise_for_status()
        return response.json()
