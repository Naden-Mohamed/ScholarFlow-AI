FROM python:3.12-slim

WORKDIR /app

COPY src/requirements.txt .

# 3. Build cache mount saves pip downloads across builds without bloating the image
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
    
COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
