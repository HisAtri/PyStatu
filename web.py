from flask import Flask, render_template, jsonify
import psutil
import time
from collections import deque
from datetime import datetime
import threading

app = Flask(__name__)

# Store the last three hours of data
data_points = deque(maxlen=3 * 60)  # Assuming data is collected every minute

def record_data():
    last_bandwidth = None
    while True:
        cpu_percent = psutil.cpu_percent()
        current_bandwidth = psutil.net_io_counters()
        memory = psutil.virtual_memory().percent
        timestamp = datetime.now()

        if last_bandwidth is not None:
            delta_bandwidth = {
                'bytes_sent': current_bandwidth.bytes_sent - last_bandwidth.bytes_sent,
                'bytes_recv': current_bandwidth.bytes_recv - last_bandwidth.bytes_recv
            }
        else:
            delta_bandwidth = {
                'bytes_sent': 0,
                'bytes_recv': 0
            }

        data_points.append({
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'bandwidth': delta_bandwidth,
            'memory': memory
        })

        last_bandwidth = current_bandwidth
        time.sleep(60)  # Record data every minute

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return jsonify(list(data_points))

if __name__ == '__main__':
    data_thread = threading.Thread(target=record_data)
    data_thread.start()
    app.run(debug=True)