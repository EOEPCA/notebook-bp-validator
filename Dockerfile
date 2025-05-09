FROM python:3.13-alpine

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install .

ENTRYPOINT ["nb-validator"]
