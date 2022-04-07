import collections
import itertools
import logging
import smtplib
import time
import typing as t
from email.mime.text import MIMEText

import arrow
import click
import jinja2
from crontab import CronTab
from insights_app.alerts_client import AlertsClient
from insights_app.smtp_client import smtp_client


INSIGHTS_DELTA = {"days": -2}
logger = logging.getLogger(__name__)

DJANGO_DT_FORMAT = "YYYY-MM-DDTHH:mm:ss"


def select_price_minmax(from_dt: arrow.Arrow, alerts_client: AlertsClient):
    """Select the earliest and the latest occurency of each item for each alert."""
    # Get lists of records for each combination of email, item_id and currency
    # Sorted by updated_date (ascended)
    results = alerts_client.get_alert_items(
        updated_at__gte=from_dt.format(DJANGO_DT_FORMAT),
        ordering="alert__email,item_id,currency,updated_at",
    )

    groups = [
        (group_key, list(vals))
        for group_key, vals in itertools.groupby(
            results, key=lambda item: (item.alert.email, item.item_id, item.currency)
        )
    ]

    # For each group get earliest and latest record
    groups = [(group_key, (vals[0], vals[-1])) for group_key, vals in groups]

    return groups


def prepare_email_data(groups, decrease_percent: float) -> t.Dict[str, t.List[t.Dict]]:
    """Analyse items to find price decrease."""
    if decrease_percent < 0 or decrease_percent > 1:
        raise ValueError("Decrease percent should be in [0;1] range")

    # For each user create list of changed items
    email_data = collections.defaultdict(list)
    for group_key, (earliest_item, latest_item) in groups:
        email, _, currency = group_key
        old_price = earliest_item.price
        new_price = latest_item.price

        if new_price > old_price * (1 - decrease_percent):
            logger.debug("Skip %s > %s * %s", new_price, old_price, decrease_percent)
            continue

        email_data[email].append(
            {
                "currency": currency,
                "old_price": old_price,
                "new_price": new_price,
                "title": latest_item.title,
                "web_url": latest_item.web_url,
            }
        )

    logger.debug("Send email data %s", email_data)
    return email_data


def send_emails(
    smtp: smtplib.SMTP,
    email_data: t.Dict[str, t.List[t.Dict]],
    sender_email: str,
):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("insights_app"),
        autoescape=jinja2.select_autoescape(),
    )
    template = env.get_template("price_decrease_email.html.j2")

    for receiver_email, items in email_data.items():
        content = template.render(items=items)
        message = MIMEText(content, "html")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Insights about your alerts"
        smtp.sendmail(sender_email, receiver_email, message.as_string())


def price_decrease_job(
    alerts_client: AlertsClient,
    smtp: smtplib.SMTP,
    sender_email: str,
    decrease_percent: int,
):
    from_dt = arrow.utcnow().shift(**INSIGHTS_DELTA)
    groups = select_price_minmax(from_dt=from_dt, alerts_client=alerts_client)
    email_data = prepare_email_data(groups=groups, decrease_percent=decrease_percent)
    send_emails(smtp=smtp, email_data=email_data, sender_email=sender_email)


@click.command(name="price_decrease_job")
@click.option("--schedule", envvar="SCHEDULE")
@click.option("--email-host", envvar="EMAIL_HOST")
@click.option("--email-port", envvar="EMAIL_PORT", type=int)
@click.option("--email-host-user", envvar="EMAIL_HOST_USER")
@click.option("--email-host-password", envvar="EMAIL_HOST_PASSWORD")
@click.option("--sender-email", envvar="SENDER_EMAIL")
@click.option("--alerts-svc-url", envvar="ALERTS_SVC_URL")
@click.option("--decrease-percent", envvar="DECREASE_PERCENT", type=float, default=0.02)
def cli(
    schedule,
    email_host,
    email_port,
    email_host_user,
    email_host_password,
    sender_email,
    alerts_svc_url,
    decrease_percent,
):
    alerts_client = AlertsClient(url=alerts_svc_url)
    scheduler = CronTab(schedule)

    while True:
        time.sleep(scheduler.next(default_utc=True))
        click.echo("Start task")
        with smtp_client(
            email_host,
            email_port,
            email_host_user,
            email_host_password,
        ) as smtp:
            price_decrease_job(
                alerts_client,
                smtp,
                sender_email,
                decrease_percent,
            )
        click.echo("OK")


if __name__ == "__main__":
    cli()
