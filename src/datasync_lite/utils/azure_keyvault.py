#! /usr/bin/env python
# -*- coding: utf-8 -*-
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

class AzureKeyVaultClient:
    def __init__(self, keyvault_url):
        self.client = SecretClient(vault_url=keyvault_url, credential=DefaultAzureCredential())

    def get_secret(self, secret_name):
        try:
            return self.client.get_secret(secret_name).value
        except ResourceNotFoundError:
            raise ValueError(f"Secret {secret_name} not found in Key Vault")
