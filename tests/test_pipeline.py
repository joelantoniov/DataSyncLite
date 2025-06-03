#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from datasync_lite.etl.pipeline import Pipeline
from unittest.mock import Mock
from pyspark.sql import SparkSession

@pytest.fixture
def spark():
    return SparkSession.builder.appName("Test").getOrCreate()

@pytest.fixture
def pipeline(spark):
    sql_client = Mock()
    sql_client.execute_query.return_value = [
        {"sales_id": 1, "sales_amount": 100, "date": "2025-06-01", "updated_at": "2025-06-01 10:00:00"}
    ]
    spark_utils = Mock()
    spark_utils.spark = spark
    config = {
        'azure': {'storage_account': 'testlake'},
        'data_quality': {'rules_file': 'configs/data_quality_rules.yaml'},
        'logging': {'log_level': 'INFO', 'azure_monitor_enabled': False},
        'pipeline_id': 'test-pipeline',
        'spark': {'executor_memory': '2g', 'executor_cores': 2, 'shuffle_partitions': 10}
    }
    logger = Mock()
    return Pipeline(sql_client, spark_utils, config, logger)

def test_pipeline_extract(pipeline):
    data = pipeline.extract()
    assert len(data) == 1
    assert pipeline.logger.info.called

def test_pipeline_transform(pipeline, spark):
    data = [{"sales_id": 1, "sales_amount": 100, "date": "2025-06-01", "updated_at": "2025-06-01 10:00:00"}]
    df = pipeline.transform(data)
    assert df.count() == 1
    assert "daily_sales" in df.columns

def test_pipeline_run(pipeline):
    pipeline.run()
    assert pipeline.logger.info.called
    assert pipeline.sql_client.execute_query.called
