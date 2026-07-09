import os
from dotenv import load_dotenv
load_dotenv()

def main():
    model = os.getenv("EMBED_MODEL")
    if not model:
        raise ValueError("EMBED_MODEL is not set")
    
    base_url = os.getenv("OLLAMA_BASE_URL")
    if not base_url:
        raise ValueError("OLLAMA_BASE_URL is not set")

if __name__ == "__main__":
    main()