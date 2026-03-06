FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
