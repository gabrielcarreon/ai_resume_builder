from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

import os
from dotenv import load_dotenv

load_dotenv()

vector_store=PGVectorStore(
            connection_string=os.getenv("DATABASE_URL"),
            table_name="ai_resume_builder",
        )

def create_pipeline(parser):
    pipeline = IngestionPipeline(
        transformations=[parser],
        vector_store=vector_store
    )
    return pipeline

def load_file(file):
    if file is None:
        raise ValueError("No file uploaded")
    reader = SimpleDirectoryReader(input_files=[file.value])
    return reader.load_data()

def main(file, parser):
    documents = load_file(file)
    pipeline = create_pipeline(parser)
    pipeline.run(documents=documents)

if __name__ == "__main__":
    main()