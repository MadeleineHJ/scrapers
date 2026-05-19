import scrapy
from google.cloud import bigquery
from scraper.items import ScrapedItem


class FootballStandingsSpider(scrapy.Spider):
    name                      = "football_standings"
    allowed_domains           = ["api.football-data.org"]
    bigquery_write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    LEAGUE = "PL"
    SEASON = "2025"

    custom_settings = {
        "DOWNLOAD_DELAY": 6,   # football-data.org free tier rate limit
    }

    def start_requests(self):
        import os
        api_key = os.environ["FOOTBALL_API_KEY"]
        url = (
            f"https://api.football-data.org/v4"
            f"/competitions/{self.LEAGUE}/standings"
            f"?season={self.SEASON}"
        )
        yield scrapy.Request(
            url=url,
            headers={"X-Auth-Token": api_key},
            callback=self.parse,
        )

    def parse(self, response):
        data = response.json()

        for standing in data.get("standings", []):
            standing_type = standing.get("type")

            for entry in standing.get("table", []):
                yield ScrapedItem(
                    extraction_type = self.name,
                    endpoint        = response.url,
                    start_date      = self.SEASON,
                    end_date        = self.SEASON,
                    data            = {
                        "standing_type": standing_type,
                        "team_id":       entry.get("team", {}).get("id"),
                        "season":        self.SEASON,
                        "raw_json":      entry,
                    },
                )