FROM python:3.10-slim as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim
WORKDIR /code
ENV TZ=Asia/Taipei
COPY --from=requirements-stage /tmp/requirements.txt .
RUN apt-get update && apt-get -y install gcc
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./app /code/app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
