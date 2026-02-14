// FluentEdge — Azure Infrastructure (Bicep)
// メインテンプレート: 全リソースのオーケストレーション

targetScope = 'resourceGroup'

@allowed(['dev', 'staging', 'production'])
param environment string
param location string = resourceGroup().location
param projectName string = 'fluentedge'

// 環境別設定
var envConfig = {
  dev: {
    containerCpu: '0.5'
    containerMemory: '1.0Gi'
    minReplicas: 0
    maxReplicas: 3
    pgSku: 'Standard_B2ms'
    pgTier: 'Burstable'
    pgStorageGB: 32
    pgHaMode: 'Disabled'
    redisSku: 'Basic'
    redisCapacity: 0
  }
  staging: {
    containerCpu: '1.0'
    containerMemory: '2.0Gi'
    minReplicas: 1
    maxReplicas: 5
    pgSku: 'Standard_D2s_v3'
    pgTier: 'GeneralPurpose'
    pgStorageGB: 64
    pgHaMode: 'Disabled'
    redisSku: 'Standard'
    redisCapacity: 1
  }
  production: {
    containerCpu: '2.0'
    containerMemory: '4.0Gi'
    minReplicas: 2
    maxReplicas: 20
    pgSku: 'Standard_D4s_v3'
    pgTier: 'GeneralPurpose'
    pgStorageGB: 256
    pgHaMode: 'ZoneRedundant'
    redisSku: 'Standard'
    redisCapacity: 2
  }
}

var config = envConfig[environment]
var resourcePrefix = '${projectName}-${environment}'

// Container Registry
module acr 'modules/container-registry.bicep' = {
  name: 'acr'
  params: {
    name: replace('${projectName}${environment}acr', '-', '')
    location: location
  }
}

// Key Vault
module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  params: {
    name: '${resourcePrefix}-kv'
    location: location
  }
}

// PostgreSQL Flexible Server
module postgresql 'modules/postgresql.bicep' = {
  name: 'postgresql'
  params: {
    name: '${resourcePrefix}-pg'
    location: location
    skuName: config.pgSku
    skuTier: config.pgTier
    storageSizeGB: config.pgStorageGB
    haMode: config.pgHaMode
    administratorLogin: 'fluentedgeadmin'
    databaseName: 'fluentedge'
    keyVaultName: keyVault.outputs.name
  }
}

// Redis Cache
module redis 'modules/redis.bicep' = {
  name: 'redis'
  params: {
    name: '${resourcePrefix}-redis'
    location: location
    skuName: config.redisSku
    capacity: config.redisCapacity
    keyVaultName: keyVault.outputs.name
  }
}

// Container Apps Environment
module containerApps 'modules/container-apps.bicep' = {
  name: 'containerApps'
  params: {
    environmentName: '${resourcePrefix}-cae'
    location: location
    backendImageName: '${acr.outputs.loginServer}/fluentedge-backend:latest'
    frontendImageName: '${acr.outputs.loginServer}/fluentedge-frontend:latest'
    containerCpu: config.containerCpu
    containerMemory: config.containerMemory
    minReplicas: config.minReplicas
    maxReplicas: config.maxReplicas
    acrLoginServer: acr.outputs.loginServer
    keyVaultName: keyVault.outputs.name
  }
}

output acrLoginServer string = acr.outputs.loginServer
output keyVaultName string = keyVault.outputs.name
output backendUrl string = containerApps.outputs.backendUrl
output frontendUrl string = containerApps.outputs.frontendUrl
