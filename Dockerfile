FROM python:3.13-slim-bookworm

WORKDIR /var/www/html

COPY app/requirements.txt .

RUN pip install --no-cache-dir uv \
    && uv pip install --system -r requirements.txt

COPY app/ .

EXPOSE 8000

ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=8000
ENV PYTHONUNBUFFERED=1

CMD ["watchmedo", "auto-restart", "--debug-force-polling", "--interval=1", "--directory=/var/www/html", "--pattern=*.py", "--", "python", "main.py"]
