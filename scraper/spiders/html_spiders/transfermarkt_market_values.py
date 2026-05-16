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


class TransfermarktMarketValuesSpider(scrapy.Spider):
    name            = "transfermarkt_market_values"
    allowed_domains = ["transfermarkt.com"]
    custom_settings = {
        "DOWNLOAD_DELAY":           3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def start_requests(self):
        for league_slug, league_id in LEAGUES.items():
            url = (
                f"https://www.transfermarkt.com/{league_slug}"
                f"/marktwerte/wettbewerb/{league_id}"
            )
            yield scrapy.Request(
                url=url,
                headers=HEADERS,
                callback=self.parse_market_values,
                meta={
                    "league":     league_slug,
                    "league_id":  league_id,
                    "page":       1,
                },
            )

    def parse_market_values(self, response):
        """Extract player market values from the league page."""
        league = response.meta["league"]
        page   = response.meta["page"]

        rows = response.css("table.items tbody tr.odd, table.items tbody tr.even")

        for row in rows:
            yield ScrapedItem(
                extraction_type = self.name,
                endpoint        = response.url,
                start_date      = None,
                end_date        = None,
                data            = {
                    "league":        league,
                    "page":          page,
                    "player_name":   row.css("td.hauptlink a::text").get("").strip(),
                    "club_name":     row.css("td.hauptlink.no-border-links a::text").get("").strip(),
                    "position":      row.css("td:nth-child(2) table tr:nth-child(2) td::text").get("").strip(),
                    "nationality":   row.css("td.zentriert img.flaggenrahmen::attr(title)").get("").strip(),
                    "age":           row.css("td.zentriert:nth-child(5)::text").get("").strip(),
                    "market_value":  row.css("td.rechts.hauptlink a::text").get("").strip(),
                },
            )

        # handle pagination -- follow next page if it exists
        next_page = response.css("li.naechste-seite a::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                headers=HEADERS,
                callback=self.parse_market_values,
                meta={
                    "league":    league,
                    "league_id": response.meta["league_id"],
                    "page":      page + 1,
                },
            )