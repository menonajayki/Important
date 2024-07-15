import cv2
import os


def extract_frames(video_path, output_folder, interval):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = int(fps * interval)

    frame_count = 0
    image_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            image_path = os.path.join(output_folder, f"10_{image_count:04d}.jpg")
            cv2.imwrite(image_path, frame)
            image_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted {image_count} images to {output_folder}")


video_path = '10.mp4'
output_folder = 'RawImages'
interval=5
extract_frames(video_path, output_folder, interval)
