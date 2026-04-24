# backend/tasks/anomaly_tasks.py

from celery import Celery
from backend.utils.prophet_helper import OutbreakDetector
from backend.models.anomaly import Anomaly
from backend.utils.alert import send_gmail_alert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Celery app initialization
celery_app = Celery('pulse')
celery_app.config_from_object('backend.celery_config')

@celery_app.task(name='tasks.run_outbreak_detection')
def run_outbreak_detection(location: str = None):
    """
    Celery task: Run anomaly detection every 6 hours.
    Triggered by scheduler, NOT manually.
    
    Flow:
    1. Get last 100 days of case data for location
    2. Train Prophet on first 80 days
    3. Detect anomalies in last 20 days
    4. Store anomalies in database
    5. If severe, send alert to Gmail
    """
    from backend.database import SessionLocal
    
    try:
        logger.info(f"Starting anomaly detection for {location}")
        
        # Get locations to check
        locations = [location] if location else get_all_locations()
        
        with SessionLocal() as session:
            for loc in locations:
                # Get case data from M4's data pipeline
                case_data = get_case_data(loc, days=100)
                
                if len(case_data) < 60:
                    logger.warning(f"Insufficient data for {loc}")
                    continue
                
                # Train detector
                detector = OutbreakDetector(loc)
                if not detector.train(case_data[:80]):
                    continue
                
                # Detect anomalies
                anomalies = detector.detect_anomalies(case_data[80:])
                
                # Store in database
                for anomaly in anomalies:
                    db_entry = Anomaly(
                        location=loc,
                        date=anomaly['ds'],
                        actual_cases=anomaly['y'],
                        predicted_cases=anomaly['yhat'],
                        severity=anomaly['anomaly_severity'],
                        confidence_interval_lower=anomaly['yhat_lower'],
                        confidence_interval_upper=anomaly['yhat_upper']
                    )
                    session.add(db_entry)
                    
                    # Alert if severe
                    if anomaly['anomaly_severity'] > 0.7:
                        subject = f"🚨 OUTBREAK ALERT: {loc}"
                        body = (
                            f"Date: {anomaly['ds']}\n"
                            f"Actual: {anomaly['y']} cases\n"
                            f"Expected: {anomaly['yhat']} cases\n"
                            f"Severity: {anomaly['anomaly_severity']:.0%}"
                        )
                        send_gmail_alert(subject, body)
                
            session.commit()
            logger.info(f"Stored anomalies for {loc}")
    
    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")
        raise

def get_case_data(location: str, days: int = 100) -> list:
    """Fetch case data from M4's data pipeline or database."""
    # This will be provided by M4
    # Expected format: [{'date': '2026-01-01', 'cases': 100}, ...]
    pass

def get_all_locations() -> list:
    """Get all locations from database."""
    # Query all unique locations with cases
    pass