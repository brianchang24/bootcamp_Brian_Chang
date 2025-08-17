import os
from dotenv import load_dotenv

def load_env():
    """Load variables from .env file."""
    load_dotenv()

def get_key(name: str, default=None):
    """Fetch a key (API, path, etc.) from environment variables."""
    return os.getenv(name, default)

def get_data_dir(default="./data"):
    """Standard accessor for the project data directory."""
    return os.getenv("DATA_DIR", default)

if __name__ == "__main__":
    load_env()
    print("API_KEY present:", get_key("API_KEY") is not None)
    print("DATA_DIR:", get_data_dir())
