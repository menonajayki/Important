import cv2
import base64
import json
import numpy as np
import paho.mqtt.client as mqtt


# MQTT broker details
broker = "localhost"
port = 1883
topic = "camera/video"

# Function to decode base64 to image
def decode_image(base64_str):
    # Decode base64 string
    img_data = base64.b64decode(base64_str)
    # Convert to numpy array
    np_arr = np.frombuffer(img_data, np.uint8)
    # Decode image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

# Callback function when a message is received
def on_message(client, userdata, msg):
    # Parse JSON message
    json_payload = json.loads(msg.payload)
    # Extract base64 image string
    base64_image = json_payload["data"]["content"]["value"]
    # Decode image
    frame = decode_image(base64_image)
    # Display image
    cv2.imshow("Live Video", frame)
    cv2.waitKey(1)

# Setup MQTT client
client = mqtt.Client()
client.on_message = on_message

# Connect to broker and subscribe to topic
client.connect(broker, port, 60)
client.subscribe(topic)

# Start MQTT loop
client.loop_start()

try:
    while True:
        # Keep the script running to display video
        cv2.waitKey(100)

except KeyboardInterrupt:
    # Cleanup
    client.loop_stop()
    client.disconnect()
    cv2.destroyAllWindows()
