import os
from dotenv import load_dotenv

def load_env() -> None:
    """Load environment variables from a local .env file."""
    load_dotenv()

def get_key(name: str, default: str | None = None) -> str | None:
    """Read a key from environment variables."""
    return os.getenv(name, default)

def get_data_dir(default: str = "./data") -> str:
    """Convenience accessor for the data directory."""
    return os.getenv("DATA_DIR", default)

if __name__ == "__main__":
    load_env()
    print("API_KEY present:", get_key("API_KEY") is not None)
    print("DATA_DIR:", get_data_dir())
