#! /usr/bin/env python
# -*- coding: utf-8 -*-
from azure.monitor.opentelemetry import configure_azure_monitor
import logging
from opentelemetry import metrics
from opentelemetry.metrics import get_meter

class Logger:
    def __init__(self, config):
        self.log_level = getattr(logging, config['log_level'])
        if config['azure_monitor_enabled']:
            configure_azure_monitor()
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger("DataSyncLite")
        self.meter = get_meter("DataSyncLite")
        self.pipeline_runs = self.meter.create_counter("pipeline_runs", description="Number of pipeline runs")
        self.pipeline_errors = self.meter.create_counter("pipeline_errors", description="Number of pipeline errors")

    def info(self, message, extra=None):
        self.logger.info(message, extra=extra)
        if extra and 'pipeline_id' in extra:
            self.pipeline_runs.add(1, {"pipeline_id": extra['pipeline_id']})

    def error(self, message, extra=None):
        self.logger.error(message, extra=extra)
        if extra and 'pipeline_id' in extra:
            self.pipeline_errors.add(1, {"pipeline_id": extra['pipeline_id']})
