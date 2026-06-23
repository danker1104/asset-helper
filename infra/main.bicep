@description('Environment name used as a resource name prefix.')
param environmentName string

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Tags applied to provisioned resources.')
param tags object = {}

@description('Bank API public key.')
@secure()
param bankApiKey string = ''

@description('Bank API secret key.')
@secure()
param bankApiSecretKey string = ''

var suffix = uniqueString(subscription().id, resourceGroup().id, environmentName)
var workspaceName = 'law-${environmentName}-${suffix}'
var managedEnvironmentName = 'cae-${environmentName}'
var apiContainerAppName = 'ca-${environmentName}-api'
var webContainerAppName = 'ca-${environmentName}-web'
var normalizedEnvName = toLower(replace(environmentName, '-', ''))
var acrBaseName = 'acr${normalizedEnvName}${suffix}'
var acrName = length(acrBaseName) > 50 ? substring(acrBaseName, 0, 50) : acrBaseName

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: managedEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

resource apiContainerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiContainerAppName
  location: location
  tags: union(tags, {
    'azd-service-name': 'api'
  })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      secrets: [
        {
          name: 'acr-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
        {
          name: 'bankapi-api-key'
          value: bankApiKey
        }
        {
          name: 'bankapi-secret-key'
          value: bankApiSecretKey
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'BANKAPI_API_KEY'
              secretRef: 'bankapi-api-key'
            }
            {
              name: 'BANKAPI_SECRET_KEY'
              secretRef: 'bankapi-secret-key'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

resource webContainerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: webContainerAppName
  location: location
  tags: union(tags, {
    'azd-service-name': 'web'
  })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      secrets: [
        {
          name: 'acr-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      ingress: {
        external: true
        targetPort: 3000
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: 'web'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'NEXT_PUBLIC_API_BASE_URL'
              value: 'https://${apiContainerApp.properties.configuration.ingress.fqdn}'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.properties.loginServer
output API_ENDPOINT string = 'https://${apiContainerApp.properties.configuration.ingress.fqdn}'
output WEB_ENDPOINT string = 'https://${webContainerApp.properties.configuration.ingress.fqdn}'
