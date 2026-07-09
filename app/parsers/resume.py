from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

import os

def main():
    return SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=OllamaEmbedding(
            model_name=os.getenv("EMBED_MODEL"),
            base_url=os.getenv("OLLAMA_BASE_URL"),
        )
    )

if __name__ == "__main__":
    main()