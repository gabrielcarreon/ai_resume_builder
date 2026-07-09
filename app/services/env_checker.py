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
    
    embed_dim = os.getenv("EMBED_DIM")
    if not embed_dim:
        raise ValueError("EMBED_DIM is not set")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set")

if __name__ == "__main__":
    main()