import yaml
import os
from langchain_google_genai import ChatGoogleGenerativeAI
path = os.path.join(os.path.dirname(__file__), "production_config.yaml")

with open(path, 'r') as file:
    project_config = yaml.safe_load(file)

llm = ChatGoogleGenerativeAI(model=project_config['llm']['model_name'], temperature=project_config['llm']['temperature'])