from common_lib.clients.ebay_client import EbayClient

from . import settings


ebay_client = EbayClient(
    app_id=settings.EBAY_APP_ID,
    cert_id=settings.EBAY_CERT_ID,
    api_url=settings.EBAY_API_URL,
)
