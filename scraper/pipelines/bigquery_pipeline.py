# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import uuid
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()


class BigQueryPipeline:
    """Writes all scraped items to a single raw table in BigQuery."""

    def __init__(self):
        self.client  = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
        self.dataset = os.environ["BQ_DATASET"]
        self.table   = f"{os.environ['GCP_PROJECT_ID']}.{self.dataset}.raw"

    def process_item(self, item, spider):
        row = {
            "run_id":          str(uuid.uuid4()),
            "data":            json.dumps(dict(item.get("data", {}))),
            "extraction_type": item.get("extraction_type", spider.name),
            "execution_date":  datetime.now(timezone.utc).isoformat(),
            "start_date":      item.get("start_date", None),
            "end_date":        item.get("end_date", None),
            "endpoint":        item.get("endpoint", None),
        }

        errors = self.client.insert_rows_json(self.table, [row])
        if errors:
            spider.logger.error(f"BigQuery insert errors: {errors}")
        else:
            spider.logger.info(f"Wrote 1 row to {self.table}")

        return item