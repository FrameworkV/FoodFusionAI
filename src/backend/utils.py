import yaml
import os

path = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(path, 'r') as file:
    config = yaml.safe_load(file)