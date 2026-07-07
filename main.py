import gradio as gr

def main():
    return "Hello, World!"



interface = gr.Interface(
    fn=main,
    inputs=["text"],
    outputs=["text"],
    title="Hello World App",
)

interface.launch(server_name="127.0.0.1", server_port=7860)