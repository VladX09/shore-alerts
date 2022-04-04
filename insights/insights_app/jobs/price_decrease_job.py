import logging
import smtplib
import time

import click
from crontab import CronTab
from insights_app.alerts_client import AlertsClient
from insights_app.smtp_client import smtp_client


logger = logging.getLogger(__name__)


def price_decrease_job(alert_client: AlertsClient, smtp: smtplib.SMTP):
    pass


@click.command(name="price_decrease_job")
@click.option("--schedule", envvar="SCHEDULE")
@click.option("--email_host", envvar="EMAIL_HOST")
@click.option("--email_port", envvar="EMAIL_PORT", type=int)
@click.option("--email_host_user", envvar="EMAIL_HOST_USER")
@click.option("--email_host_password", envvar="EMAIL_HOST_PASSWORD")
@click.option("--alerts_svc_url", envvar="ALERTS_SVC_URL")
def cli(
    schedule,
    email_host,
    email_port,
    email_host_user,
    email_host_password,
    alerts_svc_url,
):
    alerts_client = AlertsClient(url=alerts_svc_url)
    scheduler = CronTab(schedule)

    while True:
        time.sleep(scheduler.next())
        with smtp_client(
            email_host,
            email_port,
            email_host_user,
            email_host_password,
        ) as smtp:
            price_decrease_job(alerts_client, smtp)

    pass
