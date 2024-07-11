import json
import math
import paho.mqtt.client as mqtt

# MQTT broker details
broker = "10.198.153.105"
port = 1883

# Topics
topics = [
    "enterprise/workCenter/station/controlDevice/fieldDevice/gs1:4054977:NTBOSCH12595A:000171100555.accelerometer-1.X/processData/measuringValue",
    "enterprise/workCenter/station/controlDevice/fieldDevice/gs1:4054977:NTBOSCH12595A:000171100555.accelerometer-1.Y/processData/measuringValue",
    "enterprise/workCenter/station/controlDevice/fieldDevice/gs1:4054977:NTBOSCH12595A:000171100555.accelerometer-1.Z/processData/measuringValue"
]

# Global variables to store the sensor data
rawData_X, rawData_Y, rawData_Z = None, None, None

# Conversion factor
conversion_factor = 3.9


# Callback when the client receives a message
def on_message(client, userdata, msg):
    global rawData_X, rawData_Y, rawData_Z
    payload = json.loads(msg.payload.decode())
    value = payload['data']['content']['value']
    exponent = payload['data']['content']['exponent']
    adjusted_value = value * (10 ** exponent)

    if "accelerometer-1.X" in msg.topic:
        rawData_X = adjusted_value
    elif "accelerometer-1.Y" in msg.topic:
        rawData_Y = adjusted_value
    elif "accelerometer-1.Z" in msg.topic:
        rawData_Z = adjusted_value

    # Check if all values are received
    if rawData_X is not None and rawData_Y is not None and rawData_Z is not None:
        calculate_and_print_values()


# Calculate pitch, roll, and yaw
def calculate_and_print_values():
    global rawData_X, rawData_Y, rawData_Z
    ax = int(rawData_X * conversion_factor)
    ay = int(rawData_Y * conversion_factor)
    az = int(rawData_Z * conversion_factor)

    pitch = 180 * math.atan(ax / math.sqrt(ay * ay + az * az)) / math.pi
    roll = 180 * math.atan(ay / math.sqrt(ax * ax + az * az)) / math.pi
    yaw = 180 * math.atan(az / math.sqrt(ax * ax + az * az)) / math.pi

    print(f"ax: {ax}, ay: {ay}, az: {az}")
    print(f"Pitch: {pitch:.2f} degrees")
    print(f"Roll: {roll:.2f} degrees")
    print(f"Yaw: {yaw:.2f} degrees")

    # Reset values for next round of data
    rawData_X, rawData_Y, rawData_Z = None, None, None


# Create an MQTT client and attach our routines to it
client = mqtt.Client()
client.on_message = on_message

client.connect(broker, port, 60)

# Subscribe to the topics
for topic in topics:
    client.subscribe(topic)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_forever()
