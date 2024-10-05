import os
import random
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Shared parameters (mock example)
parameters = [random.random() for _ in range(5)]  # Example: 5 model parameters

# Environment configuration
role = os.getenv('ROLE', 'worker')
master_ip = os.getenv('MASTER_IP', 'localhost')
worker_id = os.getenv('WORKER_ID', '1')

@app.route('/params', methods=['GET'])
def get_params():
    """ Returns the current parameters """
    return jsonify(parameters)

@app.route('/update', methods=['POST'])
def update_params():
    """ Update parameters (for worker nodes) """
    global parameters
    updates = request.json.get('updates', [])
    # HOGWILD! style: update parameters without locks
    for i, update in enumerate(updates):
        parameters[i] += update  # Simple SGD update rule
    print(f"Master updated parameters: {parameters}")  # Print parameters after update
    return jsonify({"status": "updated"}), 200

def worker_task():
    """ Worker task: Simulate SGD updates """
    global parameters
    while True:
        # Get current parameters from the master
        response = requests.get(f'http://{master_ip}:5000/params')
        current_params = response.json()

        # Perform local SGD update
        updates = [random.uniform(-0.1, 0.1) for _ in current_params]  # Mock update

        # Send updates back to the master
        requests.post(f'http://{master_ip}:5000/update', json={'updates': updates})

        print(f"Worker {worker_id} sent updates: {updates}")  # Print worker's updates
        time.sleep(2)

if __name__ == '__main__':
    if role == 'master':
        print("Master node started...")
        app.run(host='0.0.0.0', port=5000)
    else:
        print(f"Worker {worker_id} started, connecting to master at {master_ip}...")
        worker_task()
