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

SCHEMA = [
    bigquery.SchemaField("run_id",          "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("data",            "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("extraction_type", "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("execution_date",  "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("start_date",      "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("end_date",        "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("endpoint",        "STRING",    mode="NULLABLE"),
]


class BigQueryPipeline:
    """Writes each spider's items to its own table in the scrapers dataset.
    Creates the dataset and table automatically if they do not exist.
    """

    def __init__(self):
        self.client  = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
        self.dataset  = os.environ["BQ_DATASET"]
        self._ensure_dataset()
        self._table_cache = set()   # tracks which tables have been created this run

    def _ensure_dataset(self):
        """Create the dataset if it does not exist."""
        dataset_ref = self.client.dataset(self.dataset)
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            self.client.create_dataset(dataset_ref)

    def _ensure_table(self, table_id):
        """Create the table if it does not exist."""
        if table_id in self._table_cache:
            return  # already checked this run, skip the API call

        try:
            self.client.get_table(table_id)
        except Exception:
            table = bigquery.Table(table_id, schema=SCHEMA)
            self.client.create_table(table)

        self._table_cache.add(table_id)

    def process_item(self, item, spider):
        table_id = (
            f"{os.environ['GCP_PROJECT_ID']}"
            f".{self.dataset}"
            f".{spider.name}"
        )

        self._ensure_table(table_id)

        row = {
            "run_id":           str(uuid.uuid4()),
            "data":             json.dumps(item.get("data", {})),
            "extraction_type":  item.get("extraction_type", spider.name),
            "execution_date":   datetime.now(timezone.utc).isoformat(),
            "start_date":       item.get("start_date", None),
            "end_date":         item.get("end_date", None),
            "endpoint":         item.get("endpoint", None),
        }

        errors = self.client.insert_rows_json(table_id, [row])
        if errors:
            spider.logger.error(f"BigQuery insert errors for {table_id}: {errors}")
        else:
            spider.logger.info(f"Wrote 1 row to {table_id}")

        return item