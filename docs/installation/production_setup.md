# Production Deployment Guide

## Kubernetes Requirements
- Cluster v1.25+
- Helm 3.12+
- 8 GB RAM per node
- Persistent storage class configured

## Deployment Steps

1. Add Helm repository:
```bash
helm repo add hyperion https://charts.hyperion.ai
```

2. Install release:
```bash
helm install hyperion-prod hyperion/hyperion \
  --namespace hyperion \
  --values values-production.yaml
```

3. Verify deployment:
```bash
kubectl get pods -n hyperion
```

## Configuration Values
| Parameter | Description | Default |
|-----------|-------------|---------|
| replicaCount | API server replicas | 3 |
| vectorDB.milvus.replicas | Milvus read nodes | 5 |
| autoscaling.enabled | Horizontal pod autoscaler | true |