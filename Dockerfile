FROM python:3.12-slim

# install make along with gcc and libffi-dev and clean up the package lists to reduce the final image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends make gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml Makefile /app/
RUN pip install poetry
# install in the global environment
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . /app/
RUN make all
EXPOSE 8000
CMD ["uvicorn", "application.app:app", "--host", "0.0.0.0", "--port", "8000"]
