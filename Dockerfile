FROM  python:3.8.2-slim

COPY . /app

WORKDIR app

RUN pip install -r requirements.txt && \
    mkdir -p output && \
    mkdir -p input && \
    mkdir -p tmp && \
    pip install gunicorn && \
    chmod 777 boot.sh

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]