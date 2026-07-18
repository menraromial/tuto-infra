FROM docker.io/library/python:3.12-slim

# Le SHA du commit est passé par le pipeline : --build-arg GIT_SHA=...
ARG GIT_SHA=dev
ENV GIT_SHA=$GIT_SHA

WORKDIR /app
RUN pip install --no-cache-dir 'flask==3.1.*'
COPY main.py .
EXPOSE 8000
CMD ["python", "main.py"]
