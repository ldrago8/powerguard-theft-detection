FROM python:3.12-slim

# Hugging Face Spaces requires non-root user
RUN useradd -m -u 1000 user

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV DEPLOYMENT_ENV=cloud
ENV PYTHONUTF8=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

USER user

RUN python data/generate_dataset.py && python ml/train_model.py

EXPOSE 7860

CMD uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-7860}
