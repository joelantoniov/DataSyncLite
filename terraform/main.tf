provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "datasynclite" {
  name     = "datasynclite-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "datasynclite" {
  name                = "datasynclite-vnet"
  resource_group_name = azurerm_resource_group.datasynclite.name
  location            = azurerm_resource_group.datasynclite.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "databricks" {
  name                 = "databricks-subnet"
  resource_group_name  = azurerm_resource_group.datasynclite.name
  virtual_network_name = azurerm_virtual_network.datasynclite.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_databricks_workspace" "datasynclite" {
  name                        = "datasynclite-workspace"
  resource_group_name         = azurerm_resource_group.datasynclite.name
  location                    = azurerm_resource_group.datasynclite.location
  sku                         = "premium"
  managed_resource_group_name = "datasynclite-managed-rg"
}

resource "azurerm_sql_server" "datasynclite" {
  name                         = "datasynclite-sqlserver"
  resource_group_name          = azurerm_resource_group.datasynclite.name
  location                     = azurerm_resource_group.datasynclite.location
  version                      = "12.0"
  administrator_login          = "prod_user"
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_sql_database" "sales_db" {
  name                = "sales_db"
  resource_group_name = azurerm_resource_group.datasynclite.name
  location            = azurerm_resource_group.datasynclite.location
  server_name         = azurerm_sql_server.datasynclite.name
  sku_name            = "S0"
}

resource "azurerm_sql_firewall_rule" "allow_azure" {
  name                = "AllowAzureServices"
  resource_group_name = azurerm_resource_group.datasynclite.name
  server_name         = azurerm_sql_server.datasynclite.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

resource "azurerm_storage_account" "datalake" {
  name                     = "proddatalake"
  resource_group_name      = azurerm_resource_group.datasynclite.name
  location                 = azurerm_resource_group.datasynclite.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  is_hns_enabled           = true
  min_tls_version          = "TLS1_2"
}

resource "azurerm_key_vault" "datasynclite" {
  name                        = "datasynclite-keyvault"
  resource_group_name         = azurerm_resource_group.datasynclite.name
  location                    = azurerm_resource_group.datasynclite.location
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "premium"
  purge_protection_enabled    = true
  enable_rbac_authorization   = true
}

resource "azurerm_monitor_diagnostic_setting" "sql_audit" {
  name                       = "sql-audit-logs"
  target_resource_id         = azurerm_sql_server.datasynclite.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.datasynclite.id
  log {
    category = "SQLSecurityAuditEvents"
    enabled  = true
  }
}

resource "azurerm_log_analytics_workspace" "datasynclite" {
  name                = "datasynclite-logs"
  resource_group_name = azurerm_resource_group.datasynclite.name
  location            = azurerm_resource_group.datasynclite.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}
