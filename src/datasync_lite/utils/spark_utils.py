#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession

class SparkUtils:
    def __init__(self, cluster_id, spark_config):
        self.spark = SparkSession.builder \
            .appName("DataSyncLite") \
            .config("spark.databricks.cluster.id", cluster_id) \
            .config("spark.executor.memory", spark_config['executor_memory']) \
            .config("spark.executor.cores", spark_config['executor_cores']) \
            .config("spark.dynamicAllocation.enabled", "true") \
            .config("spark.sql.shuffle.partitions", spark_config['shuffle_partitions']) \
            .getOrCreate()
