FROM python:3.10.20-alpine3.23

WORKDIR /var/www/html

COPY . .

RUN pip install uv \
    ; uv add -r /var/www/html/requirements.txt


EXPOSE 8000