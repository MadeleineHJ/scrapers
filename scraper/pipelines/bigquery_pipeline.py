# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()


class BigQueryPipeline:
    """Receives items from spiders and writes them to BigQuery."""

    def __init__(self):
        self.client  = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
        self.dataset = os.environ["BQ_DATASET"]

    def process_item(self, item, spider):
        table_id = (
            f"{os.environ['GCP_PROJECT_ID']}"
            f".{self.dataset}"
            f".{spider.name}"
        )

        row = dict(item)
        row["scraped_at"] = datetime.now(timezone.utc).isoformat()

        # convert any nested dicts/lists to JSON strings for BigQuery
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                row[key] = json.dumps(value)

        errors = self.client.insert_rows_json(table_id, [row])
        if errors:
            spider.logger.error(f"BigQuery insert errors for {table_id}: {errors}")
        else:
            spider.logger.info(f"Successfully wrote 1 row to {table_id}")

        return item