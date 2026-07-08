from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

import os
from dotenv import load_dotenv

load_dotenv()

vector_store=PGVectorStore(
            connection_string=os.getenv("DATABASE_URL")
        )

def create_pipeline():
    pipeline = IngestionPipeline(
        transformations=[
            SemanticSplitterNodeParser(
                buffer_size=1,
                breakpoiint_percentile_threshold=95,
                embed_model="nomic-embed-text"
            ),
           
        ],
        vector_store=vector_store
    )
    return pipeline

def load_file(file):
    reader = SimpleDirectoryReader(input_files=[file])
    return reader.load_data()

def main(file):
    file = load_file(file)
    pipeline = create_pipeline()
    pipeline.run(documents=file)

if __name__ == "__main__":
    main()