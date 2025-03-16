# Helm Values Reference

## Core Configuration
```yaml
# values-production.yaml
global:
  environment: prod
  domain: api.yourcompany.com

api:
  replicas: 3
  resources:
    limits:
      memory: 2Gi
  ingress:
    enabled: true

milvus:
  cluster:
    enabled: true
    etcd:
      replicaCount: 3
    pulsar:
      replicaCount: 2
  standalone: 
    enabled: false

redis:
  master:
    persistence:
      size: 20Gi