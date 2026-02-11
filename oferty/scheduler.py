"""
Automatyczne generowanie raportow zgodnie z ustawa deweloperska.
Uruchamia raportuj_auto codziennie o 6:00 rano.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

logger = logging.getLogger(__name__)

scheduler = None


def run_daily_report():
    """Generuje raporty dzienne (CSV, XLSX, JSON-LD, metadata.xml)"""
    try:
        logger.info("[scheduler] Rozpoczynam automatyczne generowanie raportow...")
        call_command('raportuj_auto')
        logger.info("[scheduler] Raporty wygenerowane pomyslnie.")
    except Exception as e:
        logger.error(f"[scheduler] Blad generowania raportow: {e}")


def start_scheduler():
    """Uruchamia scheduler - wywolywane z apps.py ready()"""
    global scheduler

    if scheduler is not None:
        return

    scheduler = BackgroundScheduler()

    # Codziennie o 6:00 rano (czas Warsaw)
    scheduler.add_job(
        run_daily_report,
        trigger=CronTrigger(hour=6, minute=0, timezone="Europe/Warsaw"),
        id="daily_report",
        name="Dzienny raport ofert deweloperskich",
        replace_existing=True,
    )

    # Uruchom tez raz przy starcie serwera (po 60 sekundach)
    from apscheduler.triggers.date import DateTrigger
    from datetime import datetime, timedelta
    scheduler.add_job(
        run_daily_report,
        trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=60)),
        id="startup_report",
        name="Raport przy starcie serwera",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[scheduler] APScheduler uruchomiony - raporty codziennie o 6:00.")
