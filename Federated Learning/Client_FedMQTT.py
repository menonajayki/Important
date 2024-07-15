import paho.mqtt.client as mqtt
import json

# MQTT Configuration
BROKER = 'mqtt.eclipseprojects.io'  # Public MQTT broker for testing
DISCOVERY_TOPIC = 'disc/fl/voicerecog'
INFO_TOPIC = 'info/fl/voicerecog/AB123/CD456'

# FL Client Payload
client_payload = {
    "n": "clientid", "v": "EF789",
    "e": [
        {"n": "26241", "v": "50"},      # Battery Level
        {"n": "26242", "v": "500"},     # CPU Speed
        {"n": "26243", "v": "3"},       # Free Memory
        {"n": "26244", "v": "500000"},  # Dataset Size
        {"n": "26245", "v": "600000"},  # Entries
        {"n": "26246", "v": "150"},     # Link Quality
        {"n": "26247", "v": "6500"}     # Position
    ]
}

def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))
    client.subscribe(DISCOVERY_TOPIC)

def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))
    discovery_message = json.loads(msg.payload)
    # Evaluate suitability (skipped for brevity)
    client.publish(INFO_TOPIC, json.dumps(client_payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()
