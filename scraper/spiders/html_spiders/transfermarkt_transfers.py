import scrapy
from scraper.items import ScrapedItem


LEAGUES = {
    "premier-league": "GB1",
    "laliga":         "ES1",
    "bundesliga":     "L1",
    "serie-a":        "IT1",
    "ligue-1":        "FR1",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":         "https://www.transfermarkt.com/",
}

# seasons to scrape -- add more as needed
SEASONS = ["2024", "2023", "2022"]


class TransfermarktTransfersSpider(scrapy.Spider):
    name            = "transfermarkt_transfers"
    allowed_domains = ["transfermarkt.com"]
    custom_settings = {
        "DOWNLOAD_DELAY":           3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def start_requests(self):
        for league_slug, league_id in LEAGUES.items():
            for season in SEASONS:
                url = (
                    f"https://www.transfermarkt.com/{league_slug}"
                    f"/transfers/wettbewerb/{league_id}"
                    f"/plus/?saison_id={season}"
                )
                yield scrapy.Request(
                    url=url,
                    headers=HEADERS,
                    callback=self.parse_transfers,
                    meta={
                        "league":  league_slug,
                        "season":  season,
                    },
                )

    def parse_transfers(self, response):
        """Extract all transfers from a league/season page."""
        league = response.meta["league"]
        season = response.meta["season"]

        # each club has an arrivals and departures box
        boxes = response.css("div.large-8.columns div.box")

        for box in boxes:
            club_name = box.css("h2.content-box-headline a::text").get("").strip()
            if not club_name:
                continue

            # arrivals
            for row in box.css("div.transfers-show table.items tr.odd, "
                               "div.transfers-show table.items tr.even"):
                yield ScrapedItem(
                    extraction_type = self.name,
                    endpoint        = response.url,
                    start_date      = f"{season}-07-01",
                    end_date        = f"{season}-06-30",
                    data            = {
                        "league":          league,
                        "season":          season,
                        "club_name":       club_name,
                        "transfer_type":   "arrival",
                        "player_name":     row.css("td.hauptlink a::text").get("").strip(),
                        "position":        row.css("td:nth-child(2) table tr:nth-child(2) td::text").get("").strip(),
                        "nationality":     row.css("td.zentriert img.flaggenrahmen::attr(title)").get("").strip(),
                        "age":             row.css("td.zentriert:nth-child(4)::text").get("").strip(),
                        "market_value":    row.css("td.rechts::text").get("").strip(),
                        "transfer_fee":    row.css("td.rechts.hauptlink a::text").get("").strip(),
                        "from_club":       row.css("td.no-border-links.vereinsname a::text").get("").strip(),
                        "to_club":         club_name,
                    },
                )

            # departures
            for row in box.css("div.transfers-hide table.items tr.odd, "
                               "div.transfers-hide table.items tr.even"):
                yield ScrapedItem(
                    extraction_type = self.name,
                    endpoint        = response.url,
                    start_date      = f"{season}-07-01",
                    end_date        = f"{season}-06-30",
                    data            = {
                        "league":          league,
                        "season":          season,
                        "club_name":       club_name,
                        "transfer_type":   "departure",
                        "player_name":     row.css("td.hauptlink a::text").get("").strip(),
                        "position":        row.css("td:nth-child(2) table tr:nth-child(2) td::text").get("").strip(),
                        "nationality":     row.css("td.zentriert img.flaggenrahmen::attr(title)").get("").strip(),
                        "age":             row.css("td.zentriert:nth-child(4)::text").get("").strip(),
                        "market_value":    row.css("td.rechts::text").get("").strip(),
                        "transfer_fee":    row.css("td.rechts.hauptlink a::text").get("").strip(),
                        "from_club":       club_name,
                        "to_club":         row.css("td.no-border-links.vereinsname a::text").get("").strip(),
                    },
                )