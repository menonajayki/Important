import paho.mqtt.client as mqtt
import base64

# Configuration
broker = 'localhost'
port = 1883
topic = 'your_topic'
received_data = b""

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    global received_data
    encoded_data = msg.payload.decode('utf-8')
    received_data += base64.b64decode(encoded_data)
    print("Received part of the encoded file")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    with open('test_recieved.pt', 'wb') as f:
        f.write(received_data)
    print("File received and written successfully.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(broker, port, 60)
client.loop_forever()
