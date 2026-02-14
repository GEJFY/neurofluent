// Azure Database for PostgreSQL Flexible Server

param name string
param location string
param skuName string
param skuTier string
param storageSizeGB int
param haMode string
param administratorLogin string
param databaseName string
param keyVaultName string

@secure()
param administratorPassword string = newGuid()

resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: name
  location: location
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    version: '16'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    storage: {
      storageSizeGB: storageSizeGB
    }
    highAvailability: {
      mode: haMode
    }
  }

  // pgvector 拡張機能を有効化
  resource pgvector 'configurations' = {
    name: 'azure.extensions'
    properties: {
      value: 'vector'
      source: 'user-override'
    }
  }
}

// データベース作成
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  parent: pg
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// 接続文字列を Key Vault に保存
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource dbConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'database-url'
  properties: {
    value: 'postgresql+asyncpg://${administratorLogin}:${administratorPassword}@${pg.properties.fullyQualifiedDomainName}:5432/${databaseName}?sslmode=require'
  }
}

output serverName string = pg.name
output fqdn string = pg.properties.fullyQualifiedDomainName
