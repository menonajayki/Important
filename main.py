import cv2
import time
from ultralytics import YOLO
import yaml
from ultralytics.utils.plotting import Annotator
import paho.mqtt.client as mqtt
import base64
import json
import numpy as np

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def decode_image(base64_str):
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

# Global variable to store the latest frame
frame = None

def on_message(client, userdata, msg):
    global frame
    json_payload = json.loads(msg.payload)
    base64_image = json_payload["data"]["content"]["value"]
    frame = decode_image(base64_image)

def main():
    config = load_config('config.yaml')
    modelpt = config['model']
    delay = config['delay']
    broker = config['broker']
    port = config['port']
    topic = config['topic']
    print(modelpt)

    model = YOLO(modelpt)

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.subscribe(topic)
    client.loop_start()

    all_detected_objects = []

    try:
        while True:
            # Run YOLOv8 inference on the frame
            results = model.track(frame)

            print("start")
            print(results)
            print("end")

            # Extracting names and bounding boxes
            for result in results:
                boxes = result.boxes
                names = result.names

                if boxes is not None and names is not None:
                    for i, box in enumerate(boxes):
                        if box is not None and len(box) > 0:
                            object_info = (names[0], box)  # Assuming names are indexed similarly to boxes
                            all_detected_objects.append(object_info)

                            # Write extracted names and boxes to a text file immediately after detection
                            with open('detected_objects.txt', 'w') as file:
                                for obj in all_detected_objects:
                                    file.write(f"Detected Object: {obj[0]}, Box: {obj[1]}\n")

            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)

            # Check for the window close event or 'q' key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or cv2.getWindowProperty("YOLOv8 Inference", cv2.WND_PROP_VISIBLE) < 1:
                break

            # Delay for the specified time
            time.sleep(delay)

    finally:
        # Cleanup
        client.loop_stop()
        client.disconnect()
        cv2.destroyAllWindows()

        # Write the final list of detected objects to a file
        with open('all_detected_objects.txt', 'w') as file:
            for obj in all_detected_objects:
                file.write(f"Detected Object: {obj[0]}, Box: {obj[1]}\n")

if __name__ == "__main__":
    main()
