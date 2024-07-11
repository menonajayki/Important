import argparse
import warnings
import flwr as fl
import numpy as np
from typing import List, Tuple, Dict, Union, Optional
from ultralytics import YOLO
import torch
import os

parser = argparse.ArgumentParser(description="Flower Embedded devices")
parser.add_argument(
    "--server_address",
    type=str,
    default="192.168.0.185:8080",
    help=f"gRPC server address (default '192.168.0.185:8080')",
)
parser.add_argument(
    "--cid",
    type=int,
    required=True,
    help="Client id. Should be an integer between 0 and NUM_CLIENTS",
)

warnings.filterwarnings("ignore", category=UserWarning)
NUM_CLIENTS = 50

def load_data(client_id: int):
    data_path = f"client{client_id}.yaml"
    return data_path

def load_model():
    net = YOLO('yolov8n.pt')  # Use YOLOv8n pre-trained model
    return net

def train(net, data, epochs: int):
    net.train(data=data, epochs=epochs, imgsz=640, batch=4, plots=False, device=0)

def test(net):
    metrics = net.val(data='global.yaml')
    map50 = metrics.box.map50
    return map50

def set_parameters(net: YOLO, parameters: List[np.ndarray]) -> None:
    for i, param in enumerate(net.model.parameters()):
        param_ = torch.from_numpy(parameters[i]).to(param.device)
        param.data.copy_(param_)

def get_parameters(net: YOLO) -> List[np.ndarray]:
    return [param.data.cpu().numpy() for param in net.model.parameters()]

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, net, data_path):
        self.net = net
        self.data_path = data_path

    def get_parameters(self, config):
        return get_parameters(self.net)

    def fit(self, parameters, config):
        set_parameters(self.net, parameters)
        train(self.net, data=self.data_path, epochs=config["epochs"])
        return get_parameters(self.net), len(self.net.model.parameters()), {}

    def evaluate(self, parameters, config):
        set_parameters(self.net, parameters)
        map50 = test(self.net)
        return map50, len(self.net.model.parameters()), {"map50": map50}

def main():
    args = parser.parse_args()

    net = load_model()
    data_path = load_data(args.cid)

    fl.client.start_numpy_client(
        server_address=args.server_address,
        client=FlowerClient(net, data_path),
    )

if __name__ == "__main__":
    main()
