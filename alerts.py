import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import subprocess
import json

# Import the Metric model from your central API server module
# from central_server_app import Metric  # Adjust this import based on your project structure
# For this example, we'll define a simple Metric model placeholder:
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String

Base = declarative_base()
class Metric(Base):
    __tablename__ = 'metric'
    id = Column(Integer, primary_key=True)
    hostname = Column(String(100))
    timestamp = Column(Float)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_usage_percent = Column(Float)
    net_io = Column(String)      # Stored as JSON string
    load_avg = Column(String)    # Stored as string representation

# Configuration
DATABASE_URI = 'sqlite:///metrics.db'  # Adjust if using PostgreSQL, etc.
ALERT_THRESHOLD_CPU = 75.0             # CPU usage threshold in percent
ALERT_DURATION = 120                   # Duration in seconds (2 minutes)
EMAIL_RECIPIENT = "admin@example.com"
EMAIL_SENDER = "monitor@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "smtp_username"
SMTP_PASSWORD = "smtp_password"

# Set up database session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def send_email_alert(subject, body):
    """Send an email alert using SMTP."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send alert email: {e}")

def remediate_issue(issue_type):
    """Execute remediation action based on issue type."""
    if issue_type == "high_cpu":
        print("Executing remediation for high CPU: Restarting the critical service.")
        # Example: Restart a service (e.g., 'example_service')
        try:
            subprocess.run(["sudo", "systemctl", "restart", "example_service"], check=True)
            print("Service restarted successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Remediation failed: {e}")

def check_alerts():
    """Query recent metrics and check for alert conditions."""
    now = datetime.now()
    threshold_time = now - timedelta(seconds=ALERT_DURATION)
    # Retrieve metrics from the last ALERT_DURATION seconds
    metrics = session.query(Metric).filter(Metric.timestamp >= threshold_time.timestamp()).all()
    if not metrics:
        print("No recent metrics to evaluate.")
        return

    # Check if all collected metrics indicate high CPU usage
    high_cpu = all(metric.cpu_percent > ALERT_THRESHOLD_CPU for metric in metrics)
    if high_cpu:
        subject = "High CPU Alert"
        body = (f"CPU usage has been above {ALERT_THRESHOLD_CPU}% for the past "
                f"{ALERT_DURATION // 60} minutes on host {metrics[0].hostname}.")
        print("Alert condition met, sending email and triggering remediation.")
        send_email_alert(subject, body)
        remediate_issue("high_cpu")
    else:
        print("No alert condition met.")

if __name__ == "__main__":
    print("Starting alerting engine...")
    while True:
        try:
            check_alerts()
        except Exception as e:
            print(f"Error during alert check: {e}")
        # Check alerts every 60 seconds
        time.sleep(60)
