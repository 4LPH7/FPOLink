"""FPOLink TN — Background Worker

Runs scheduled tasks in a separate container.
Does NOT run inside the API process to avoid duplicate jobs with multiple workers.
"""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_price_ingestion():
    """Fetch daily prices from configured data sources."""
    logger.info("Running price ingestion...")
    # TODO: Import and call ingestion service
    logger.info("Price ingestion complete.")


def run_weather_ingestion():
    """Fetch weather data from Open-Meteo / NASA POWER."""
    logger.info("Running weather ingestion...")
    # TODO: Import and call weather service
    logger.info("Weather ingestion complete.")


def run_predictions():
    """Generate price forecasts using the active model."""
    logger.info("Running predictions...")
    # TODO: Import and call prediction service
    logger.info("Predictions complete.")


def run_daily_digest():
    """Daily price digest sent to opted-in farmers at 07:30 IST (T4.2)."""
    import asyncio

    from app.api.whatsapp import get_wa_settings
    from app.messaging.whatsapp_cloud import WhatsAppCloudChannel
    from app.services.whatsapp_digest import DailyDigestService

    logger.info("Starting WhatsApp daily digest run...")
    cfg = get_wa_settings()
    channel = WhatsAppCloudChannel(cfg.access_token, cfg.phone_number_id, cfg.api_version)
    service = DailyDigestService()
    metrics = asyncio.run(service.run_digest(channel))
    logger.info("Daily digest completed: %s", metrics)


def run_price_alerts():
    """Price-move alerts sent to opted-in farmers at 07:45 IST (T4.3)."""
    import asyncio

    from app.api.whatsapp import get_wa_settings
    from app.messaging.whatsapp_cloud import WhatsAppCloudChannel
    from app.services.whatsapp_alerts import PriceMoveAlertService

    logger.info("Starting WhatsApp price-move alerts check...")
    cfg = get_wa_settings()
    channel = WhatsAppCloudChannel(cfg.access_token, cfg.phone_number_id, cfg.api_version)
    service = PriceMoveAlertService()
    metrics = asyncio.run(service.check_and_send_alerts(channel))
    logger.info("Price-move alerts completed: %s", metrics)


def run_data_retention():
    """DPDP retention purge at 03:00 IST (T5.3)."""
    from app.services.retention import (
        purge_conversation_state,
        purge_inbound,
        purge_outbound,
    )

    logger.info("Starting data retention purge...")
    purge_inbound(retention_days=7)
    purge_conversation_state(ttl_hours=24)
    purge_outbound(retention_months=12)
    logger.info("Data retention purge complete.")


def run_inbound_sweep():
    """At-least-once sweep for stuck inbound messages (T5.4)."""
    from app.services.inbound_sweep import sweep_stuck_inbound

    metrics = sweep_stuck_inbound()
    if metrics["found"] > 0:
        logger.info("Inbound sweep: %s", metrics)


def main():
    from app.config import settings

    if settings.SENTRY_DSN:
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
            logger.info("Sentry initialized in worker (env=%s)", settings.ENVIRONMENT)
        except ImportError:
            logger.warning("sentry-sdk not installed; skipping worker Sentry initialization")

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Daily at 3 AM IST — DPDP data retention purge (T5.3)
    scheduler.add_job(run_data_retention, "cron", hour=3, minute=0, id="data_retention")

    # Daily at 5 AM IST — weather
    scheduler.add_job(run_weather_ingestion, "cron", hour=5, minute=0, id="weather_ingestion")

    # Daily at 6 AM IST — prices
    scheduler.add_job(run_price_ingestion, "cron", hour=6, minute=0, id="price_ingestion")

    # Daily at 7 AM IST — predictions (after fresh prices)
    scheduler.add_job(run_predictions, "cron", hour=7, minute=0, id="predictions")

    # Daily at 7:30 AM IST — WhatsApp price digest (T4.2)
    scheduler.add_job(run_daily_digest, "cron", hour=7, minute=30, id="whatsapp_daily_digest")

    # Daily at 7:45 AM IST — WhatsApp price-move alerts (T4.3)
    scheduler.add_job(run_price_alerts, "cron", hour=7, minute=45, id="whatsapp_price_alerts")

    # Every 10 minutes — at-least-once inbound sweep (T5.4)
    scheduler.add_job(run_inbound_sweep, "interval", minutes=10, id="inbound_sweep")

    logger.info("FPOLink Worker started. Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  {job.id}: {job.trigger}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker shutting down.")


if __name__ == "__main__":
    main()
