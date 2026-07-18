# Build multi-stage : les dépendances sont installées dans une première
# étape, seule l'image finale (légère) est conservée.
FROM docker.io/library/python:3.12-slim AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM docker.io/library/python:3.12-slim
WORKDIR /app
COPY --from=deps /install /usr/local
COPY main.py .
EXPOSE 8000
CMD ["python", "main.py"]
