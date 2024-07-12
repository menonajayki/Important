import cv2
import time
from ultralytics import YOLO
import yaml


def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Load the training.yaml
    config = load_config('../training.yaml')
    delay = 2
    modelpt = 'trained200.pt'

    print(modelpt)

    model = YOLO(modelpt)

    # 0 - default webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        last_capture_time = time.time()-5
        # Loop through the video frames
        while True:
            current_time = time.time()

            # Read a frame only every 5 seconds
            if current_time - last_capture_time >= delay:
                success, frame = cap.read()
                last_capture_time = current_time

                if not success:
                    print("Error: Could not read frame from webcam.")
                    break

                # Run YOLOv8 inference on the frame
                results = model.track(frame, conf=0.2)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()

                # Display the annotated frame
                cv2.imshow("YOLOv8 Inference", annotated_frame)

            # Check for the window close event or 'q' key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or cv2.getWindowProperty("YOLOv8 Inference", cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        # Release the webcam and close the display window
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()




