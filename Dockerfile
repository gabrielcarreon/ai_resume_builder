FROM python:3.13-slim-bookworm

WORKDIR /var/www/html

COPY app/ .

RUN pip install --no-cache-dir uv

EXPOSE 8000

ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=8000
ENV PYTHONUNBUFFERED=1

CMD ["source", "/var/www/html/.venv/bin/activate", "&&", "gradio", "app/main.py"]
