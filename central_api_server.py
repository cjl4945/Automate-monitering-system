# MIT License
# Copyright (c) [2025] [Chase Lewis]


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)

# Configure database URI (use PostgreSQL or another DB in production)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///metrics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# API key for authentication, set via environment variable in production
API_KEY = os.environ.get('API_KEY', 'your_api_key_here')

# Database model for storing metrics
class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    timestamp = db.Column(db.Float)
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    disk_usage_percent = db.Column(db.Float)
    net_io = db.Column(db.Text)      # Stored as JSON string
    load_avg = db.Column(db.String(50))  # Stored as string representation

    def __repr__(self):
        return f"<Metric {self.hostname} at {datetime.fromtimestamp(self.timestamp)}>"

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    # Validate API key from the Authorization header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized: Missing or invalid token'}), 401
    token = auth_header.split(' ')[1]
    if token != API_KEY:
        return jsonify({'error': 'Unauthorized: Invalid API key'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid payload: No JSON provided'}), 400

    try:
        # Create a new Metric entry from the payload
        metric = Metric(
            hostname=data.get('hostname'),
            timestamp=data.get('timestamp'),
            cpu_percent=data.get('cpu_percent'),
            memory_percent=data.get('memory_percent'),
            disk_usage_percent=data.get('disk_usage_percent'),
            net_io=json.dumps(data.get('net_io')),  # Convert dict to JSON string
            load_avg=str(data.get('load_avg'))
        )
        db.session.add(metric)
        db.session.commit()
        return jsonify({'message': 'Metrics received successfully'}), 200
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Run the server with HTTPS; replace 'cert.pem' and 'key.pem' with your certificate files
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
