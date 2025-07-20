from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import time
from threading import Thread
import json

app = Flask(__name__)

# Global variables to store sensor data
sensor_data = {
    'temperature': 36.5,
    'gas': 120,
    'sound': 45,
    'status': 'live',  # live, deceased, uncertain
    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# Detection history log
detection_history = []

# Simulate sensor data updates
def sensor_simulator():
    while True:
        # Generate random variations
        temp_variation = random.uniform(-0.2, 0.2)
        gas_variation = random.randint(-5, 5)
        sound_variation = random.randint(-3, 3)
        
        # Update sensor values with some constraints
        sensor_data['temperature'] = round(max(32, min(38, sensor_data['temperature'] + temp_variation), 1))
        sensor_data['gas'] = max(100, min(300, sensor_data['gas'] + gas_variation))
        sensor_data['sound'] = max(20, min(80, sensor_data['sound'] + sound_variation))
        
        # Determine status based on sensor values
        if sensor_data['temperature'] < 33 or sensor_data['gas'] > 250 or sensor_data['sound'] < 30:
            sensor_data['status'] = 'deceased'
        elif sensor_data['temperature'] < 34 or sensor_data['gas'] > 200 or sensor_data['sound'] < 35:
            sensor_data['status'] = 'uncertain'
        else:
            sensor_data['status'] = 'live'
        
        sensor_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add to history (only keep last 100 entries)
        detection_history.append({
            'timestamp': sensor_data['last_updated'],
            'temperature': sensor_data['temperature'],
            'gas': sensor_data['gas'],
            'sound': sensor_data['sound'],
            'status': sensor_data['status']
        })
        if len(detection_history) > 100:
            detection_history.pop(0)
        
        time.sleep(5)

# Start sensor simulator in background
Thread(target=sensor_simulator, daemon=True).start()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', 
                         sensor_data=sensor_data,
                         history=detection_history[-10:][::-1])

@app.route('/api/data')
def get_data():
    # Generate chart data (last 20 readings)
    chart_labels = [f"{i*5} sec" for i in range(20)]
    
    # Generate realistic chart data based on actual sensor values
    temp_data = [max(32, min(38, sensor_data['temperature'] + random.uniform(-0.2, 0.2))) for _ in range(20)]
    gas_data = [max(100, min(300, sensor_data['gas'] + random.randint(-5, 5))) for _ in range(20)]
    sound_data = [max(20, min(80, sensor_data['sound'] + random.randint(-3, 3))) for _ in range(20)]
    
    return jsonify({
        'labels': chart_labels,
        'datasets': [
            {
                'label': 'Temperature (°C)',
                'data': temp_data,
                'borderColor': '#ff9a9e',
                'backgroundColor': 'rgba(255, 154, 158, 0.1)',
                'tension': 0.4,
                'fill': True
            },
            {
                'label': 'Gas Level (ppm)',
                'data': gas_data,
                'borderColor': '#a18cd1',
                'backgroundColor': 'rgba(161, 140, 209, 0.1)',
                'tension': 0.4,
                'fill': True
            },
            {
                'label': 'Sound Level (dB)',
                'data': sound_data,
                'borderColor': '#84fab0',
                'backgroundColor': 'rgba(132, 250, 176, 0.1)',
                'tension': 0.4,
                'fill': True
            }
        ],
        'sensor_data': sensor_data
    })

@app.route('/api/history')
def get_history():
    return jsonify({
        'history': detection_history[::-1]  # Return in reverse chronological order
    })

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    
    if action == 'start':
        # In a real system, this would start actual monitoring
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    elif action == 'stop':
        # In a real system, this would stop actual monitoring
        return jsonify({'status': 'success', 'message': 'Monitoring stopped'})
    elif action == 'reset':
        # In a real system, this would reset alerts
        return jsonify({'status': 'success', 'message': 'Alerts reset'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'})

if __name__ == '__main__':
    app.run(debug=True)