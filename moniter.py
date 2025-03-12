# MIT License
# Copyright (c) [2025] [Chase Lewis]

import psutil
import time
import requests
import socket
import json

def collect_metrics():
    """Collect system metrics including CPU, memory, disk, network I/O, and load average."""
    metrics = {
        "hostname": socket.gethostname(),
        "timestamp": time.time(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "net_io": psutil.net_io_counters()._asdict(),
        "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
    }
    return metrics

def send_metrics(metrics, url, api_key):
    """Send the collected metrics to the monitoring server using HTTPS and API key authentication."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.post(url, json=metrics, headers=headers, timeout=5, verify=False)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Metrics sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending metrics: {e}")

if __name__ == "__main__":
    # Configuration
    MONITORING_SERVER_URL = "https://localhost:5000/api/metrics"  # Replace with your actual endpoint
    API_KEY = "your_api_key_here"  # Replace with your secure API key
    INTERVAL_SECONDS = 60  # Frequency of data collection in seconds

    while True:
        metrics = collect_metrics()
        print(f"Collected metrics: {json.dumps(metrics, indent=2)}")  # Optional: log metrics locally
        send_metrics(metrics, MONITORING_SERVER_URL, API_KEY)
        time.sleep(INTERVAL_SECONDS)
