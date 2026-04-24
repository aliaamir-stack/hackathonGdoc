# backend/utils/prophet_helper.py

import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OutbreakDetector:
    """
    Uses Facebook Prophet to detect anomalies in case count time series.
    Prophet handles seasonality, trends, and holidays automatically.
    """
    
    def __init__(self, location: str):
        self.location = location
        self.model = None
        self.forecast = None
        
    def train(self, data: list):
        """
        Train Prophet model on historical case data.
        
        data format: [
            {'date': '2026-01-01', 'cases': 10},
            {'date': '2026-01-02', 'cases': 12},
            ...
        ]
        """
        try:
            # Convert to DataFrame (Prophet requirement)
            df = pd.DataFrame(data)
            df['ds'] = pd.to_datetime(df['date'])
            df['y'] = df['cases'].astype(float)
            df = df[['ds', 'y']].sort_values('ds')
            
            # If less than 2 months of data, anomaly detection won't work well
            if len(df) < 60:
                logger.warning(f"Not enough data for {self.location}: {len(df)} days")
                return False
            
            # Create and train Prophet model
            # yearly_seasonality=True handles seasonal patterns
            # weekly_seasonality=True handles day-of-week patterns
            self.model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=0.95,  # 95% confidence interval
                changepoint_prior_scale=0.05  # Sensitivity to trend changes
            )
            
            self.model.fit(df)
            logger.info(f"Model trained for {self.location} with {len(df)} data points")
            return True
            
        except Exception as e:
            logger.error(f"Training failed for {self.location}: {str(e)}")
            return False
    
    def detect_anomalies(self, data: list, confidence_threshold: float = 0.95):
        """
        Detect anomalies in recent case data.
        
        Returns list of anomalies with:
        - date
        - actual cases
        - predicted cases
        - confidence (how sure we are it's anomalous)
        """
        if not self.model:
            return []
        
        try:
            # Prepare data
            df = pd.DataFrame(data)
            df['ds'] = pd.to_datetime(df['date'])
            df['y'] = df['cases'].astype(float)
            df = df[['ds', 'y']].sort_values('ds')
            
            # Make forecast (only need last N days)
            future = df[['ds']].copy()
            forecast = self.model.predict(future)
            
            # Merge actual vs predicted
            result = df.merge(
                forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
                on='ds'
            )
            
            # Find anomalies: points outside confidence interval
            result['is_anomaly'] = (
                (result['y'] > result['yhat_upper']) |
                (result['y'] < result['yhat_lower'])
            )
            
            # Calculate anomaly severity (0-1 score)
            result['anomaly_severity'] = 0.0
            for idx, row in result.iterrows():
                if row['is_anomaly']:
                    # How far from prediction?
                    if row['y'] > row['yhat_upper']:
                        severity = min(1.0, (row['y'] - row['yhat']) / row['yhat'])
                    else:
                        severity = min(1.0, (row['yhat'] - row['y']) / row['yhat'])
                    result.at[idx, 'anomaly_severity'] = severity
            
            # Return only anomalies
            anomalies = result[result['is_anomaly']].to_dict('records')
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return []