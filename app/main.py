import gradio as gr
import document_processor as dp

def main(resume: gr.File, skills: str):
    dp(resume.name)
    return resume


interface = gr.Interface(
    fn=main,
    inputs=[gr.File(label="Resume"), gr.File(label="Skills MD")],
    outputs=[gr.File(label="Translated Resume")],
    title="Hello World App",
)

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=8000)
