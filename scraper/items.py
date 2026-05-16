# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class ScrapedItem(scrapy.Item):
    run_id         = scrapy.Field()   # unique ID for each scrape run
    data           = scrapy.Field()   # raw payload as JSON string
    extraction_type = scrapy.Field()  # e.g. "transfermarkt_squads"
    execution_date = scrapy.Field()   # when the pipeline ran
    start_date     = scrapy.Field()   # date range start (if applicable)
    end_date       = scrapy.Field()   # date range end (if applicable)
    endpoint       = scrapy.Field()   # the URL that was scraped