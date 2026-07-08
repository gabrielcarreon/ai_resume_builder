import gradio as gr
import rag.pipeline as pipeline

def main(files):
    for file in files:
        pipeline.main(file)
    return files[0]


interface = gr.Interface(
    fn=main,
    inputs=[gr.File(label="Resume, Skills.MD etc", file_count="multiple")],
    outputs=[gr.File(label="Translated Resume")],
    title="Hello World App",
)

if __name__ == "__main__":
    interface.launch(server_name="127.0.0.1", server_port=8000)
