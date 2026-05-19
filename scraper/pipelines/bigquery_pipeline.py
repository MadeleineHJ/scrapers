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
    def __init__(self):
        self.client  = bigquery.Client(project=os.environ["GCP_PROJECT_ID"])
        self.dataset = os.environ["BQ_DATASET"]
        self._buffer      = []
        self._ensure_dataset()
        self._table_cache = set()

    def _ensure_dataset(self):
        dataset_ref = self.client.dataset(self.dataset)
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            self.client.create_dataset(dataset_ref)

    def _ensure_table(self, table_id):
        if table_id in self._table_cache:
            return
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

        self._buffer.append({
            "table_id": table_id,
            "spider":   spider,
            "row": {
                "run_id":           str(uuid.uuid4()),
                "data":             json.dumps(item.get("data", {})),
                "extraction_type":  item.get("extraction_type", spider.name),
                "execution_date":   datetime.now(timezone.utc).isoformat(),
                "start_date":       item.get("start_date", None),
                "end_date":         item.get("end_date", None),
                "endpoint":         item.get("endpoint", None),
            }
        })
        return item

    def close_spider(self, spider):
        if not self._buffer:
            spider.logger.warning("No items to load to BigQuery")
            return

        # read write disposition from spider settings
        # defaults to WRITE_APPEND unless spider sets BIGQUERY_WRITE_DISPOSITION
        write_disposition = getattr(
            spider, "bigquery_write_disposition",
            bigquery.WriteDisposition.WRITE_APPEND
        )

        tables = {}
        for entry in self._buffer:
            tables.setdefault(entry["table_id"], []).append(entry["row"])

        for table_id, rows in tables.items():
            job_config = bigquery.LoadJobConfig(
                schema            = SCHEMA,
                write_disposition = write_disposition,
                source_format     = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            )

            job = self.client.load_table_from_json(
                json_rows   = rows,
                destination = table_id,
                job_config  = job_config,
            )
            job.result()

            spider.logger.info(
                f"Batch loaded {len(rows)} rows to {table_id} "
                f"(write_disposition={write_disposition})"
            )