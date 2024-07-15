import paho.mqtt.client as mqtt
import json

# MQTT Configuration
BROKER = 'mqtt.eclipseprojects.io'  # Public MQTT broker for testing
DISCOVERY_TOPIC = 'disc/fl/voicerecog'
INFO_TOPIC = 'info/fl/voicerecog/AB123/CD456'

# FL Server Payload
server_payload = [
    {"n": "serverid", "v": "AB123"},
    {"n": "taskid", "v": "CD456"},
    {"n": "URIpath", "v": "18832/0"}
]

def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))
    client.subscribe(INFO_TOPIC)
    client.publish(DISCOVERY_TOPIC, json.dumps(server_payload))

def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))
    client_info = json.loads(msg.payload)
    # Process client_info for client selection
    print("Client Info: ", client_info)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()
