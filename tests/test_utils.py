#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from datasync_lite.utils.logger import Logger
from datasync_lite.utils.azure_keyvault import AzureKeyVaultClient
from datasync_lite.utils.sqlserver_client import SQLServerClient
from unittest.mock import Mock

def test_logger_metrics():
    config = {'log_level': 'INFO', 'azure_monitor_enabled': False}
    logger = Logger(config)
    logger.info("Test", extra={'pipeline_id': 'test-pipeline'})
    logger.error("Error", extra={'pipeline_id': 'test-pipeline'})
    assert logger.pipeline_runs.get_value() == 1
    assert logger.pipeline_errors.get_value() == 1

def test_keyvault_get_secret():
    mock_client = Mock()
    mock_client.get_secret.return_value.value = "test-secret"
    AzureKeyVaultClient.client = mock_client
    kv_client = AzureKeyVaultClient("https://test.vault.azure.net")
    secret = kv_client.get_secret("test-secret")
    assert secret == "test-secret"

def test_sqlserver_client_query():
    logger = Mock()
    sql_client = SQLServerClient("localhost", "test_db", "user", "pass", logger)
    sql_client.conn = Mock()
    sql_client.conn.cursor.return_value.description = [("id",), ("name",)]
    sql_client.conn.cursor.return_value.fetchall.return_value = [(1, "test")]
    result = sql_client.execute_query("SELECT * FROM test")
    assert result == [{"id": 1, "name": "test"}]
