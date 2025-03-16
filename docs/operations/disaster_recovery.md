# Disaster Recovery Plan

## Backup Strategy
1. **Milvus Snapshots**
```bash
milvusctl backup create --name daily-backup --collection-all
```
2. **Redis RDB Persistence**
```yaml
# redis-config.yaml
save 900 1
save 300 10
save 60 10000
dir /data
```

3. **Metadata Backups**
```sql
-- Daily PostgreSQL dump
pg_dump -U hyperion -Fc hyperion_db > /backups/hyperion-$(date +%F).dump
```

## Restoration Procedures
```mermaid
flowchart TD
    A[Identify Failure] --> B{Data Loss?}
    B -->|Yes| C[Restore Latest Backup]
    B -->|No| D[Restart Services]
    C --> E[Validate Consistency]
    E --> F[Resume Operations]