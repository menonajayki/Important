import cv2
import time
import base64
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT broker details
broker = "10.198.153.204"
port = 1883
topic = "1/2/3/4/5/gs1:4054977:6261409141030.camera-3/data"


# Function to create JSON payload
def create_json_payload(frame):
    # Encode frame to JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    # Convert to base64
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    # Create JSON structure
    payload = {
        "semantic": {
            "type": "sensors",
            "version": "1.0.0",
            "specification": "zeiss"
        },
        "security": {
            "publisher": {
                "id": "gs1:4054977:6261409141030.camera-3",
                "name": "camera",
                "location": "measuringRoom"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "signature": "123456789"
        },
        "data": {
            "id": "gs1:4054977:6261409141030.camera-3",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "category": "processData/measuringValue",
            "content": {
                "sensorType": "camera",
                "value": jpg_as_text,
                "exponent": 0,
                "unit": ""
            }
        }
    }
    return json.dumps(payload)


# Setup MQTT client
client = mqtt.Client()
client.connect(broker, port, 60)

# Capture video from camera
cap = cv2.VideoCapture(0)

try:
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Create JSON payload
        json_payload = create_json_payload(frame)

        # Publish the JSON payload
        client.publish(topic, json_payload)

        # Wait for 5 seconds
        time.sleep(2)

finally:
    # Release the camera and MQTT client
    cap.release()
    client.disconnect()
