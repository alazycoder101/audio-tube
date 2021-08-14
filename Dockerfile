# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1

ARG app=/app
WORKDIR $app

ADD . .

EXPOSE 8000
CMD ["python", "server.py"]
