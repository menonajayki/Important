import paho.mqtt.client as mqtt

# Define the broker details
broker_address = "localhost"
broker_port = 1884
topic = "ajay/workCenter/station/controlDevice/fieldDevice/gs1:4054977:6261409141070:simulatedSerialnumber/equipmentData/AAS"
message = "Hello, MQTT!"
username = "username"
password = "password"

# Create an MQTT client instance
client = mqtt.Client()

# Set username and password
client.username_pw_set(username, password)

# Connect to the broker
client.connect(broker_address, broker_port, 60)

# Publish the message
client.publish(topic, message)

# Disconnect from the broker
client.disconnect()

print("Message published successfully")
