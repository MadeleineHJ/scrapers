from scrapy.utils.project import get_project_settings
from scraper.items import ScrapedItem


def test_settings_load():
    """Check that Scrapy settings load without errors."""
    settings = get_project_settings()
    assert settings is not None


def test_pipeline_configured():
    """Check that BigQuery pipeline is registered in settings."""
    settings = get_project_settings()
    pipelines = settings.get("ITEM_PIPELINES", {})
    assert "scraper.pipelines.bigquery_pipeline.BigQueryPipeline" in pipelines


def test_scraped_item_fields():
    """Check that ScrapedItem has all required fields."""
    item = ScrapedItem()
    required_fields = [
        "run_id", "data", "extraction_type",
        "execution_date", "start_date", "end_date", "endpoint"
    ]
    for field in required_fields:
        assert field in item.fields