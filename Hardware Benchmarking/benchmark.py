import time
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO  # Replace with the actual import for YOLOv8

def benchmark_yolov8(model, input_data):
    start_time = time.time()
    results = model(input_data)
    end_time = time.time()
    for result in results:
        inference_time = result.speed
    return inference_time

def load_model(model_path):
    model = YOLO(model_path)
    return model

def run_benchmarks(model_path, input_data):
    model = load_model(model_path)
    inference_time = benchmark_yolov8(model, input_data)
    return inference_time

def main():
    # Path to the model file on the device
    model_path = 'yolov8n.pt'

    # Generate or load input data
    input_data = "img.png"  # Example input

    # Run benchmark
    inference_time = run_benchmarks(model_path, input_data)

    # Save results to a text file
    with open('benchmark_results.txt', 'w') as f:
        f.write(f"Time: {inference_time} ms")

    # Given timing results
    timings = inference_time

    # Extract the keys and values for plotting
    labels = list(timings.keys())
    times = list(timings.values())

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, times, color=['blue', 'green', 'red'])
    plt.xlabel('Stages')
    plt.ylabel('Time (ms)')
    plt.title('YOLOv8 Inference Time Breakdown')
    plt.savefig('benchmark.png')

if __name__ == "__main__":
    main()
