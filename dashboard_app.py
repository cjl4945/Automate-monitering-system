# MIT License
# Copyright (c) [2025] [Chase Lewis]

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///metrics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for metrics (should match your existing model)
class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    timestamp = db.Column(db.Float)
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    disk_usage_percent = db.Column(db.Float)
    net_io = db.Column(db.Text)      # JSON string
    load_avg = db.Column(db.String(50))  # String representation

@app.route('/')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """Return metrics data from the past 30 days as JSON."""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    metrics = Metric.query.filter(Metric.timestamp >= thirty_days_ago.timestamp()).order_by(Metric.timestamp).all()
    data = []
    for m in metrics:
        data.append({
            "timestamp": datetime.fromtimestamp(m.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": m.cpu_percent,
            "memory_percent": m.memory_percent,
            "disk_usage_percent": m.disk_usage_percent
        })
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
