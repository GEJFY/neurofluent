// Azure Container Apps Environment + Backend/Frontend Apps

param environmentName string
param location string
param backendImageName string
param frontendImageName string
param containerCpu string
param containerMemory string
param minReplicas int
param maxReplicas int
param acrLoginServer string
param keyVaultName string

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${environmentName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Container Apps Environment
resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Backend Container App
resource backend 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${environmentName}-backend'
  location: location
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      registries: [
        {
          server: acrLoginServer
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImageName
          resources: {
            cpu: json(containerCpu)
            memory: containerMemory
          }
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// Frontend Container App
resource frontend 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${environmentName}-frontend'
  location: location
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
      }
      registries: [
        {
          server: acrLoginServer
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImageName
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

output backendUrl string = 'https://${backend.properties.configuration.ingress.fqdn}'
output frontendUrl string = 'https://${frontend.properties.configuration.ingress.fqdn}'
