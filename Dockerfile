FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
ARG PORT
ENV PORT=${PORT:-8000}
EXPOSE ${PORT}  
RUN adduser --disabled-password --gecos "" appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:${PORT:-8000}/ || exit 1
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
