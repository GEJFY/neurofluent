// Azure Cache for Redis

param name string
param location string
param skuName string
param capacity int
param keyVaultName string

resource redis 'Microsoft.Cache/redis@2023-08-01' = {
  name: name
  location: location
  properties: {
    sku: {
      name: skuName
      family: skuName == 'Premium' ? 'P' : 'C'
      capacity: capacity
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisVersion: '7'
  }
}

// 接続文字列を Key Vault に保存
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource redisConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'redis-url'
  properties: {
    value: 'rediss://:${redis.listKeys().primaryKey}@${redis.properties.hostName}:${redis.properties.sslPort}/0'
  }
}

output hostName string = redis.properties.hostName
output sslPort int = redis.properties.sslPort
