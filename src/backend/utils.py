import yaml
import os
from langchain_google_genai import ChatGoogleGenerativeAI

path = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(path, 'r') as file:
    config = yaml.safe_load(file)

# automatically loads API key from the .env file
model = ChatGoogleGenerativeAI(model=config['llm']['model_name'], temperature=config['llm']['temperature'])