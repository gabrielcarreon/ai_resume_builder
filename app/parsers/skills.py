from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

import os

def main(file):
    return MarkdownNodeParser(
        include_metadata=True
    )

if __name__ == "__main__":
    main()