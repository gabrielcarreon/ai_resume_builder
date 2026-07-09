import gradio as gr
import rag.pipeline as pipeline
import parsers.resume as resume_parser
import parsers.skills as skills_parser
import services.env_checker as env_checker

def main(resume: gr.File, skills: gr.File):
    env_checker.main()
    pipeline.main(resume, resume_parser.main())

    return "Ingested"


interface = gr.Interface(
    fn=main,
    inputs=[
        gr.File(label="Resume", file_count="single"),
        gr.File(label="Skills MD", file_count="single")
    ],
    outputs=[gr.Textbox(label="Ingested")],
    title="Hello World App",
)

if __name__ == "__main__":
    interface.launch(server_name="127.0.0.1", server_port=8000)
