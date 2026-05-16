# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class HtmlPageItem(scrapy.Item):
    """For spiders that scrape HTML pages."""
    source_url  = scrapy.Field()
    scraped_at  = scrapy.Field()
    page_title  = scrapy.Field()
    raw_html    = scrapy.Field()


class ApiResponseItem(scrapy.Item):
    """For spiders that call REST APIs."""
    endpoint    = scrapy.Field()
    scraped_at  = scrapy.Field()
    status_code = scrapy.Field()
    payload     = scrapy.Field()  # raw JSON stored as a dict