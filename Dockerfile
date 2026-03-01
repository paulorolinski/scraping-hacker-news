FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY scraper.py .
COPY database.py .
COPY country.py .
COPY analysis.py .
COPY charts.py .

CMD ["python", "main.py"]