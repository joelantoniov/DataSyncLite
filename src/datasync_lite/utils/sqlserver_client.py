#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pyodbc
from retry import retry
from azure.core.exceptions import ServiceRequestError

class SQLServerClient:
    def __init__(self, host, database, username, password, logger):
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.logger = logger
        self.conn = self._connect()

    @retry(ServiceRequestError, tries=3, delay=2, backoff=2)
    def _connect(self):
        return pyodbc.connect(self.conn_str)

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.conn.commit()
            return None
        except Exception as e:
            self.logger.error(f"SQL query failed: {str(e)}")
            raise
        finally:
            cursor.close()
