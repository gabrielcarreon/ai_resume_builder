import gradio as gr
import rag.pipeline as pipeline
import parsers.resume as resume_parser
import parsers.skills as skills_parser
import services.env_checker as env_checker

def main(resume: str | None, skills: str | None):
    env_checker.main()
    counts = []
    if resume:
        counts.append(pipeline.run(resume, resume_parser.main(), "resume"))
    if skills:
        counts.append(pipeline.run(skills, skills_parser.main(), "skills"))
    return f"Ingested {sum(counts)} chunks"


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
