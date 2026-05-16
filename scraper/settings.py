# Scrapy settings for scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from dotenv import load_dotenv

load_dotenv()

# ── Project ───────────────────────────────────────────────
BOT_NAME      = "scraper"
SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# ── Crawl behaviour ───────────────────────────────────────
ROBOTSTXT_OBEY  = True
DOWNLOAD_DELAY  = 1        # seconds between requests, be polite
CONCURRENT_REQUESTS          = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# ── Retry ─────────────────────────────────────────────────
RETRY_ENABLED  = True
RETRY_TIMES    = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# ── Middlewares ────────────────────────────────────────────
DOWNLOADER_MIDDLEWARES = {
    "scraper.middlewares.ScraperDownloaderMiddleware": 543,
}

# ── Pipelines ─────────────────────────────────────────────
ITEM_PIPELINES = {
    "scraper.pipelines.bigquery_pipeline.BigQueryPipeline": 300,
}

# ── HTTP cache (speeds up development) ────────────────────
HTTPCACHE_ENABLED    = True
HTTPCACHE_EXPIRATION_SECS = 3600   # 1 hour, set to 0 to disable
HTTPCACHE_DIR        = ".scrapy/httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504]

# ── Logging ───────────────────────────────────────────────
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# ── Feed exports (optional, useful for local debugging) ───
FEEDS = {
    "output/%(name)s_%(time)s.json": {
        "format": "json",
        "overwrite": False,
    }
}