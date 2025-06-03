#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from great_expectations.dataset import SparkDFDataset
import datetime
from retry import retry
from circuitbreaker import circuit
from azure.core.exceptions import ServiceRequestError

class Pipeline:
    def __init__(self, sql_client, spark_utils, config, logger):
        self.sql_client = sql_client
        self.spark_utils = spark_utils
        self.config = config
        self.logger = logger
        self.spark = spark_utils.spark

    @retry(ServiceRequestError, tries=3, delay=2, backoff=2)
    @circuit(failure_threshold=5, recovery_timeout=60)
    def extract(self):
        query = "SELECT * FROM sales WHERE updated_at > ?"
        watermark = self._get_watermark()
        data = self.sql_client.execute_query(query, (watermark,))
        self.logger.info(f"Extracted {len(data)} records")
        return data

    def transform(self, data):
        df = self.spark.createDataFrame(data)
        df = df.na.drop(subset=["sales_id"]).filter(df.sales_amount > 0)
        df = df.groupBy("date").agg({"sales_amount": "sum"}).withColumnRenamed("sum(sales_amount)", "daily_sales")
        df.cache()
        self.logger.info(f"Transformed DataFrame with {df.count()} rows")
        return df

    def validate(self, df):
        ge_df = SparkDFDataset(df)
        rules_file = self.config['data_quality']['rules_file']
        with open(rules_file, 'r') as f:
            rules = yaml.safe_load(f)['rules']

        for rule in rules:
            expectation = rule['expectation']
            params = rule.get('params', {})
            getattr(ge_df, expectation)(rule['column'], **params)

        result = ge_df.validate()
        if not result.success:
            self.logger.error(f"Data quality validation failed: {result}")
            raise ValueError("Data quality checks failed")
        self.logger.info("Data quality validation passed")

    def load(self, df):
        output_path = f"{self.config['azure']['storage_account']}/delta/sales"
        df.write.format("delta").mode("append").option("mergeSchema", "true").save(output_path)
        self.logger.info(f"Loaded data to {output_path}")
        df.unpersist()

    def run(self):
        try:
            self.logger.info("Starting ETL pipeline", extra={"pipeline_id": self.config['pipeline_id']})
            data = self.extract()
            if not data:
                self.logger.warning("No new data to process")
                return
            df = self.transform(data)
            self.validate(df)
            self.load(df)
            self._update_watermark()
            self.logger.info("ETL pipeline completed successfully")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}", extra={"pipeline_id": self.config['pipeline_id']})
            raise

    def _get_watermark(self):
        query = "SELECT MAX(updated_at) as watermark FROM watermark_log"
        result = self.sql_client.execute_query(query)
        return result[0]['watermark'] if result else datetime.datetime(1970, 1, 1)

    def _update_watermark(self):
        watermark = datetime.datetime.now()
        query = "INSERT INTO watermark_log (watermark, pipeline_id) VALUES (?, ?)"
        self.sql_client.execute_query(query, (watermark, self.config['pipeline_id']))
