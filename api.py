from src.api.app import run
import os

if __name__ == "__main__":
    api_port = os.getenv("API_PORT")
    run(port=api_port)
