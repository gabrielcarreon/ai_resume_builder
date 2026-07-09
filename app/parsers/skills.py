from llama_index.core.node_parser import MarkdownNodeParser

def main():
    return MarkdownNodeParser(
        include_metadata=True
    )

if __name__ == "__main__":
    main()