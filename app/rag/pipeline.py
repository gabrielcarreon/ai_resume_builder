from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

import os
from pathlib import Path
from dotenv import load_dotenv


def _load_env() -> None:
    root_env = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(root_env)


def _database_urls() -> tuple[str, str]:
    sync_url = os.getenv("DATABASE_URL")
    if not sync_url:
        raise ValueError("DATABASE_URL is not set")

    async_url = os.getenv("ASYNC_DATABASE_URL")
    if not async_url:
        async_url = sync_url.replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://", 1
        )
    return sync_url, async_url


def create_pipeline(parser):
    _load_env()
    sync_url, async_url = _database_urls()
    embed_model = OllamaEmbedding(
            model_name=os.getenv("EMBED_MODEL"),
            base_url=os.getenv("OLLAMA_BASE_URL"),
        )
    vector_store = PGVectorStore(
            connection_string=sync_url,
            async_connection_string=async_url,
            table_name="ai_resume_builder",
            embed_dim=int(os.getenv("EMBED_DIM", "768")),
        )

    return IngestionPipeline(
        transformations=[parser, embed_model],
        vector_store=vector_store
    )

def load_file(file):
    if file is None:
        raise ValueError("No file uploaded")
    reader = SimpleDirectoryReader(input_files=[file])
    return reader.load_data()

def run(file, parser, doc_type: str):
    try:
        documents = load_file(file)
        for doc in documents:
            doc.metadata["doc_type"] = doc_type
        nodes = create_pipeline(parser).run(documents=documents)
        return len(nodes)
    except Exception as e:
        raise
