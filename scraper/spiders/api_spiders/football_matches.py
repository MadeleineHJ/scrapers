import scrapy
from google.cloud import bigquery
from scraper.items import ScrapedItem


class FootballMatchesSpider(scrapy.Spider):
    name                      = "football_matches"
    allowed_domains           = ["api.football-data.org"]
    bigquery_write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    LEAGUE = "PL"
    SEASON = "2025"

    custom_settings = {
        "DOWNLOAD_DELAY": 6,
    }

    def start_requests(self):
        import os
        api_key = os.environ["FOOTBALL_API_KEY"]
        url = (
            f"https://api.football-data.org/v4"
            f"/competitions/{self.LEAGUE}/matches"
            f"?season={self.SEASON}"
        )
        yield scrapy.Request(
            url=url,
            headers={"X-Auth-Token": api_key},
            callback=self.parse,
        )

    def parse(self, response):
        data = response.json()

        for match in data.get("matches", []):
            yield ScrapedItem(
                extraction_type = self.name,
                endpoint        = response.url,
                start_date      = self.SEASON,
                end_date        = self.SEASON,
                data            = {
                    "match_id": match.get("id"),
                    "season":   self.SEASON,
                    "raw_json": match,
                },
            )