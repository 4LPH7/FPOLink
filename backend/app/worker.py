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


def main():
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Daily at 5 AM IST — weather
    scheduler.add_job(run_weather_ingestion, 'cron', hour=5, minute=0, id='weather_ingestion')

    # Daily at 6 AM IST — prices
    scheduler.add_job(run_price_ingestion, 'cron', hour=6, minute=0, id='price_ingestion')

    # Daily at 7 AM IST — predictions (after fresh prices)
    scheduler.add_job(run_predictions, 'cron', hour=7, minute=0, id='predictions')

    logger.info("FPOLink Worker started. Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  {job.id}: {job.trigger}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker shutting down.")


if __name__ == "__main__":
    main()
