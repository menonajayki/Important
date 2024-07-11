import paho.mqtt.client as mqtt
import base64
import time

# Configuration
broker = 'localhost'
port = 1883
topic = 'your_topic'
publish_interval = 5  # Publish every 5 seconds

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    with open('test.pt', 'rb') as f:
        data = f.read()
        encoded = base64.b64encode(data).decode('utf-8')
        while True:
            client.publish(topic, encoded)
            print("Published encoded file")
            time.sleep(publish_interval)

client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker, port, 60)
client.loop_forever()
