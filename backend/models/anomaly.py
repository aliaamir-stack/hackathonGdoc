# backend/models/anomaly.py

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Anomaly(Base):
    """
    Stores detected anomalies.
    Referenced by alerts and dashboard.
    """
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True)
    location = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    actual_cases = Column(Float, nullable=False)
    predicted_cases = Column(Float, nullable=False)
    severity = Column(Float, nullable=False)  # 0-1 score
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'date': self.date.isoformat(),
            'actual_cases': self.actual_cases,
            'predicted_cases': self.predicted_cases,
            'severity': self.severity,
            'confidence_interval': {
                'lower': self.confidence_interval_lower,
                'upper': self.confidence_interval_upper
            }
        }