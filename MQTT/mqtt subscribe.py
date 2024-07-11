import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe("ajay/workCenter/station/controlDevice/fieldDevice/gs1:4054977:6261409141070:simulatedSerialnumber/equipmentData/AAS")
    else:
        print("Connection failed with code", rc)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client()

client.username_pw_set("username", "password")

client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
broker_address = "localhost"
broker_port = 1884
client.connect(broker_address, broker_port, 60)

# Start the loop to process network traffic and dispatch callbacks
client.loop_forever()

