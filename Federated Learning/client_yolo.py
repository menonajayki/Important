import argparse
import warnings
import flwr as fl
from ultralytics import YOLO
import torch
import os

parser = argparse.ArgumentParser(description="Flower Embedded devices")
parser.add_argument(
    "--server_address",
    type=str,
    default="192.168.0.128:8080",
    help="gRPC server address (default '0.0.0.0:8080')",
)
parser.add_argument(
    "--cid",
    type=int,
    required=True,
    help="Client id. Should be an integer between 0 and NUM_CLIENTS",
)
parser.add_argument(
    "--dataset_dir",
    type=str,
    required=True,
    help="Directory containing the dataset for this client",
)

warnings.filterwarnings("ignore", category=UserWarning)
NUM_CLIENTS = 50

class FlowerClient(fl.client.NumPyClient):
    """A FlowerClient that uses YOLOv8 for object detection."""

    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.model = YOLO('yolov8n.pt')

        # Check if CUDA is available
        if not torch.cuda.is_available():
            print("CUDA is not available. Training will proceed on the CPU.")
            self.device = 'cpu'
        else:
            print("CUDA is available. Training will proceed on the GPU.")
            self.device = 'cuda:0'

    def get_parameters(self, config):
        return self.model.model.state_dict()

    def set_parameters(self, params):
        self.model.model.load_state_dict(params)

    def fit(self, parameters, config):
        print("Client sampled for fit()")
        self.set_parameters(parameters)

        # Set hyperparameters from config sent by server/strategy
        epochs = config["epochs"]
        batch_size = config["batch_size"]

        # Train the model
        results = self.model.train(
            data=os.path.join(self.dataset_dir, 'data.yaml'),
            imgsz=640,
            epochs=epochs,
            batch=batch_size,
            plots=True,
            patience=250,
            device=self.device,
            name=f'yolov8n_client'
        )

        return self.get_parameters({}), len(os.listdir(self.dataset_dir)), {}

    def evaluate(self, parameters, config):
        print("Client sampled for evaluate()")
        self.set_parameters(parameters)

        results = self.model.val(data=os.path.join(self.dataset_dir, 'data.yaml'))
        loss = results.box_loss
        accuracy = results.box_acc

        return loss, len(os.listdir(self.dataset_dir)), {"accuracy": accuracy}


def main():
    args = parser.parse_args()
    print(args)

    assert args.cid < NUM_CLIENTS

    # Start Flower client setting its associated data partition
    fl.client.start_client(
        server_address=args.server_address,
        client=FlowerClient(
            dataset_dir=args.dataset_dir
        ).to_client(),
    )


if __name__ == "__main__":
    main()
