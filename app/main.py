import gradio as gr

def main(text: str):
    return f"Hello, {text}!reload verifiedzdddcvvv"


interface = gr.Interface(
    fn=main,
    inputs=[gr.File(label="Resume")],
    outputs=[gr.File(label="Translated Resume")],
    title="Hello World App",
)

if __name__ == "__main__":
    interface.launch(server_name="127.0.0.1", server_port=8000)
