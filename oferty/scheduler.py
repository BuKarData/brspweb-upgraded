"""
Scheduler dla automatycznego raportowania
Uruchamia management command codziennie o 6:00 rano
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def run_daily_report():
    """Uruchamia dzienny raport"""
    try:
        logger.info("Rozpoczynam automatyczny raport...")
        call_command('raportuj_auto')
        logger.info("Raport zakończony pomyślnie")
    except Exception as e:
        logger.error(f"Błąd podczas automatycznego raportu: {str(e)}")

def start_scheduler():
    """Uruchamia scheduler w tle"""
    scheduler = BackgroundScheduler()
    
    # Zadanie codzienne o 6:00
    scheduler.add_job(
        run_daily_report,
        'cron',
        hour=6,
        minute=0,
        id='daily_report_job',
        replace_existing=True
    )
    
    # Opcjonalnie: uruchom raport przy starcie aplikacji
    # scheduler.add_job(
    #     run_daily_report,
    #     'date',
    #     run_date=datetime.now() + timedelta(seconds=30)
    # )
    
    scheduler.start()
    logger.info("Scheduler uruchomiony - raporty będą generowane codziennie o 6:00")
    
    return scheduler
