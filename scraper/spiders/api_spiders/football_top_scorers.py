import scrapy
from google.cloud import bigquery
from scraper.items import ScrapedItem


class FootballTopScorersSpider(scrapy.Spider):
    name                      = "football_top_scorers"
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
            f"/competitions/{self.LEAGUE}/scorers"
            f"?season={self.SEASON}&limit=50"
        )
        yield scrapy.Request(
            url=url,
            headers={"X-Auth-Token": api_key},
            callback=self.parse,
        )

    def parse(self, response):
        data = response.json()

        for entry in data.get("scorers", []):
            yield ScrapedItem(
                extraction_type = self.name,
                endpoint        = response.url,
                start_date      = self.SEASON,
                end_date        = self.SEASON,
                data            = {
                    "player_id": entry.get("player", {}).get("id"),
                    "season":    self.SEASON,
                    "raw_json":  entry,
                },
            )