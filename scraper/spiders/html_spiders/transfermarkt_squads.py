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


class TransfermarktSquadsSpider(scrapy.Spider):
    name            = "transfermarkt_squads"
    allowed_domains = ["transfermarkt.com"]
    custom_settings = {
        "DOWNLOAD_DELAY":           3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def start_requests(self):
        for league_slug, league_id in LEAGUES.items():
            url = (
                f"https://www.transfermarkt.com/{league_slug}"
                f"/startseite/wettbewerb/{league_id}"
            )
            yield scrapy.Request(
                url=url,
                headers=HEADERS,
                callback=self.parse_league,
                meta={"league": league_slug},
            )

    def parse_league(self, response):
        """Extract all club URLs from the league page."""
        club_links = response.css(
            "table.items tbody tr td.hauptlink a::attr(href)"
        ).getall()

        for link in club_links:
            yield scrapy.Request(
                url=response.urljoin(link),
                headers=HEADERS,
                callback=self.parse_squad,
                meta={"league": response.meta["league"]},
            )

    def parse_squad(self, response):
        """Extract all players from a club squad page."""
        league    = response.meta["league"]
        club_name = response.css(
            "h1.data-header__headline-wrapper::text"
        ).get("").strip()

        rows = response.css("table.items tbody tr.odd, table.items tbody tr.even")

        for row in rows:
            yield ScrapedItem(
                extraction_type = self.name,
                endpoint        = response.url,
                start_date      = None,
                end_date        = None,
                data            = {
                    "league":       league,
                    "club_name":    club_name,
                    "player_name":  row.css("td.hauptlink a::text").get("").strip(),
                    "position":     row.css("td:nth-child(2) table tr:nth-child(2) td::text").get("").strip(),
                    "nationality":  row.css("td.zentriert img.flaggenrahmen::attr(title)").get("").strip(),
                    "age":          row.css("td.zentriert:nth-child(6)::text").get("").strip(),
                    "shirt_number": row.css("div.rn_nummer::text").get("").strip(),
                },
            )