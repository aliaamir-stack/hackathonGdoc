# In a file: test_prophet.py
from backend.utils.prophet_helper import OutbreakDetector
import pandas as pd
from datetime import datetime, timedelta

# Create test data (normal growth)
data = []
base_date = datetime(2026, 1, 1)
for i in range(100):
    date = base_date + timedelta(days=i)
    cases = 10 + i * 0.5 + (5 if i % 7 == 0 else 0)  # Normal growth + weekly spike
    data.append({'date': date.strftime('%Y-%m-%d'), 'cases': int(cases)})

# Add an anomaly (spike)
data[90] = {'date': data[90]['date'], 'cases': 200}

# Test detector
detector = OutbreakDetector('TestCity')
detector.train(data[:80])  # Train on first 80 days
anomalies = detector.detect_anomalies(data[80:])  # Test on last 20

print(anomalies)
