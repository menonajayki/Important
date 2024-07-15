import socket
import struct
import math
import json
import paho.mqtt.client as mqtt

PORT = 8382
UDP_DUMPER_HEADER1 = b'POS'
UDP_DUMPER_HEADER1_LENGTH = len(UDP_DUMPER_HEADER1)
STRUCT_FORMAT = 'Ifffffffdd'
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 8884
MQTT_TOPIC = 'sensor/location'
CA_CERTS = "mosquitto.org.crt"
CLIENT_CERT = "client.crt"
CLIENT_KEY = "client.key"
EARTH_RADIUS = 6371000


def meters_to_latlon(x, y, ref_lat, ref_lon):
    ref_lat_rad = math.radians(ref_lat)

    delta_lat = y / EARTH_RADIUS
    delta_lat_deg = math.degrees(delta_lat)
    delta_lon = x / (EARTH_RADIUS * math.cos(ref_lat_rad))
    delta_lon_deg = math.degrees(delta_lon)
    new_lat = ref_lat + delta_lat_deg
    new_lon = ref_lon + delta_lon_deg

    return new_lat, new_lon


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    client.subscribe("$SYS/#")


def on_publish(client, userdata, mid, reason_code=None):
    print("Data published")


def read_receiver_positions(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                parts = line.split('=', 1)
                if len(parts) != 2:
                    continue
                key, value = parts[0].strip(), parts[1].strip().replace(' ', '')
                if key == 'ReceiverPositions':
                    return value
    except FileNotFoundError:
        print(f"Warning: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def listen_udp(port, ref_latitude, ref_longitude, mqtt_client):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', port)
    print(f"Listening for UDP packets on port {port}...")
    sock.bind(server_address)
    expected_size = struct.calcsize(STRUCT_FORMAT)
    print(f"Expected size after header: {expected_size} bytes")
    counter = 0
    try:
        while True:
            data, address = sock.recvfrom(4096)
            if data[:UDP_DUMPER_HEADER1_LENGTH] != UDP_DUMPER_HEADER1:
                print(f"Error: Header wrong (should be '{UDP_DUMPER_HEADER1.decode()}').")
                continue
            if len(data) - UDP_DUMPER_HEADER1_LENGTH != expected_size:
                print(f"Error: Data size mismatch. Expected {expected_size}, got {len(data) - UDP_DUMPER_HEADER1_LENGTH}")
                continue
            dataPtr = data[UDP_DUMPER_HEADER1_LENGTH:]
            unpacked_data = struct.unpack(STRUCT_FORMAT, dataPtr)
            senderGUID, x, y, z, sigma, velocityX, velocityY, velocityZ, sendingTime, creationTime = unpacked_data
            counter += 1
            # Construct JSON structure
            lat, lon = meters_to_latlon(x, y, ref_latitude, ref_longitude)
            json_output = {
                "rxTime": creationTime,
                "cnt": counter,
                "algorithm": "tdoa",
                "latitude": lat,
                "longitude": lon,
                "altitude": z,
                "accuracy": [sigma, sigma, sigma]
            }
            # Convert dictionary to JSON string
            json_string = json.dumps(json_output, indent=4)
            print(json_string)
            print("Unpacked data:", unpacked_data)
            # Publish to MQTT broker
            mqtt_client.publish(MQTT_TOPIC, json_string)
    except KeyboardInterrupt:
        print("Stopped listening.")
    finally:
        sock.close()


def extract_coordinates(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                if 'geo lat' in line and 'lng' in line:
                    parts = line.split()
                    lat_index = parts.index('lat') + 1
                    lng_index = parts.index('lng') + 1
                    if lat_index < len(parts) and lng_index < len(parts):
                        return float(parts[lat_index]), float(parts[lng_index])
    except FileNotFoundError:
        print(f"Warning: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return 0, 0


if __name__ == '__main__':
    ref_lat = 0
    ref_lon = 0
    receiver_positions = read_receiver_positions('user.ini')
    if receiver_positions:
        print("Receiver Positions:", receiver_positions)
    else:
        receiver_positions = read_receiver_positions('system.ini')
    if not receiver_positions:
        print("No receivers.txt found")
    if receiver_positions:
        ref_lat, ref_lon = extract_coordinates(receiver_positions)
    print(ref_lat)
    print(ref_lon)
    # Setup MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.tls_set(ca_certs=CA_CERTS, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()
    listen_udp(PORT, ref_lat, ref_lon, mqtt_client)
