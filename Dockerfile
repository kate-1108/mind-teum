FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m playwright install --skip-deps chromium

COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
