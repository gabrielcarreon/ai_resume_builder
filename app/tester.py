import gradio as gr

def main(query: str):
    return "HELLO WORLD"

interface = gr.Interface(
    inputs=[gr.Textbox(label="Input")],
    outputs=[gr.Textbox(label="Output")],
    fn=main,
    title="Tester",
    description="This is a tester",
)

interface.launch(server_name="127.0.0.1", server_port=8081)