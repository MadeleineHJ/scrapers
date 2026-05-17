FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scrapy.cfg .
COPY scraper/ scraper/

CMD ["scrapy", "crawl", "--help"]