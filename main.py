
import os
import socket
import time
import requests
import numpy as np
from flask import Flask, request, jsonify
import docker

# Simulated placeholder for parameters (weights) and other necessary global values
parameters = [0.0]
convergence_threshold = 0.001  # Threshold for convergence
gradients = []  # List to keep track of gradients (for statistical reporting)
max_updates = 100  # Max iterations to avoid infinite runs
update_count = 0

# Flask app for master node
app = Flask(__name__)

def check_convergence():
    """Check if the gradient updates have converged."""
    if len(gradients) > 10:  # Check only after some updates
        recent_updates = gradients[-10:]
        avg_update = np.mean(np.abs(recent_updates))
        print(f"Average of last 10 updates: {avg_update}")
        return avg_update < convergence_threshold
    return False

def master():
    """Master node to receive updates from workers and apply them."""
    global parameters, update_count

    @app.route("/update", methods=["POST"])
    def update():
        global update_count, parameters, gradients
        update_value = request.json['update']
        gradients.append(update_value)  # Store the gradient for statistical analysis
        parameters[0] += update_value  # Update the parameter

        # Logging in a structured format
        print(f"\n--- Update {update_count + 1} ---")
        print(f"Received update from worker: {update_value}")
        print(f"Updated parameter value: {parameters[0]}")
        print(f"Gradient variance: {np.var(gradients)}")
        print(f"Gradient std deviation: {np.std(gradients)}")
        print(f"Total updates so far: {update_count + 1}\n")

        update_count += 1

        # Check for convergence
        if check_convergence() or update_count >= max_updates:
            print("SGD has converged or reached max updates. Stopping all workers...")
            stop_all_containers()  # Stop all containers when SGD converges
            return jsonify({"status": "converged", "parameter": parameters[0]})

        return jsonify({"status": "success", "new_parameter": parameters[0]})

    app.run(host="0.0.0.0", port=5000)

def worker(master_host):
    """Worker node to perform SGD and send updates to the master."""
    while True:
        time.sleep(2)  # Simulate computation delay
        gradient_update = np.random.normal(loc=1.0, scale=0.1)  # Simulated SGD gradient
        response = requests.post(f"http://{master_host}:5000/update", json={'update': gradient_update})
        print(f"Worker sent update {gradient_update}. Master response: {response.json()}")
        if response.json().get("status") == "converged":
            print("SGD has converged. Stopping worker.")
            break  # Stop worker if SGD has converged

def stop_all_containers():
    """Stop all running Docker containers."""
    client = docker.from_env()
    containers = client.containers.list()  # List all running containers
    for container in containers:
        print(f"Stopping container: {container.name}")
        container.stop()

if __name__ == "__main__":
    role = os.getenv("ROLE", "worker")
    if role == "master":
        print("Starting master node...")
        master()
    else:
        master_host = os.getenv("MASTER_HOST", "localhost")
        print(f"Starting worker node, connecting to master at {master_host}...")
        worker(master_host)
