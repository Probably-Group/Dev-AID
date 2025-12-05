# Harbor Performance Optimization

## Pattern 1: Garbage Collection Optimization

**Bad** - Infrequent GC causes storage bloat:
```bash
# ❌ Monthly GC - storage fills up
{
  "schedule": {
    "type": "Custom",
    "cron": "0 0 1 * *"
  },
  "parameters": {
    "delete_untagged": false
  }
}
```

**Good** - Regular GC with untagged deletion:
```bash
# ✅ Weekly GC with untagged cleanup
curl -X POST "https://harbor.example.com/api/v2.0/system/gc/schedule" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": {
      "type": "Weekly",
      "cron": "0 2 * * 6"
    },
    "parameters": {
      "delete_untagged": true,
      "dry_run": false,
      "workers": 4
    }
  }'

# Monitor GC performance
curl -s "https://harbor.example.com/api/v2.0/system/gc" \
  -u "admin:password" | jq '.[-1] | {status, deleted, duration: (.end_time - .start_time)}'
```

## Pattern 2: Replication Optimization

**Bad** - Unfiltered full replication:
```bash
# ❌ Replicate everything - wastes bandwidth
{
  "name": "replicate-all",
  "filters": [],
  "trigger": {"type": "event_based"},
  "speed": 0
}
```

**Good** - Filtered scheduled replication with bandwidth control:
```bash
# ✅ Filtered replication with scheduling and rate limiting
curl -X POST "https://harbor.example.com/api/v2.0/replication/policies" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "replicate-production",
    "filters": [
      {"type": "name", "value": "production/**"},
      {"type": "tag", "value": "v*"},
      {"type": "label", "value": "approved=true"}
    ],
    "trigger": {
      "type": "scheduled",
      "trigger_settings": {
        "cron": "0 */4 * * *"
      }
    },
    "speed": 10485760,
    "override": true,
    "enabled": true
  }'

# Monitor replication performance
curl -s "https://harbor.example.com/api/v2.0/replication/executions?policy_id=1" \
  -u "admin:password" | jq '[.[] | select(.status=="Succeed")] | length'
```

## Pattern 3: Caching and Proxy Configuration

**Bad** - No caching, direct pulls every time:
```bash
# ❌ Every pull hits upstream registry
docker pull docker.io/library/nginx:latest
# Slow and uses bandwidth
```

**Good** - Harbor as proxy cache:
```bash
# ✅ Configure proxy cache endpoint
curl -X POST "https://harbor.example.com/api/v2.0/registries" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dockerhub-cache",
    "type": "docker-hub",
    "url": "https://hub.docker.com",
    "credential": {
      "access_key": "username",
      "access_secret": "token"
    }
  }'

# Create proxy cache project
curl -X POST "https://harbor.example.com/api/v2.0/projects" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "dockerhub-proxy",
    "registry_id": 1,
    "public": true
  }'

# Pull through cache - subsequent pulls are instant
docker pull harbor.example.com/dockerhub-proxy/library/nginx:latest
```

## Pattern 4: Storage Backend Optimization

**Bad** - Local filesystem storage:
```bash
# ❌ Filesystem storage - no HA, backup complexity
storage_service:
  filesystem:
    rootdirectory: /data/registry
```

**Good** - Object storage with lifecycle policies:
```bash
# ✅ S3 storage with intelligent tiering
REGISTRY_STORAGE_PROVIDER_NAME=s3
REGISTRY_STORAGE_PROVIDER_CONFIG='{
  "bucket": "harbor-artifacts",
  "region": "us-east-1",
  "rootdirectory": "/harbor",
  "storageclass": "INTELLIGENT_TIERING",
  "multipartcopythresholdsize": 33554432,
  "multipartcopychunksize": 33554432,
  "multipartcopymaxconcurrency": 100,
  "encrypt": true,
  "v4auth": true
}'

# Configure lifecycle policy for old artifacts
aws s3api put-bucket-lifecycle-configuration \
  --bucket harbor-artifacts \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "archive-old-artifacts",
      "Status": "Enabled",
      "Filter": {"Prefix": "harbor/"},
      "Transitions": [{
        "Days": 90,
        "StorageClass": "GLACIER"
      }],
      "NoncurrentVersionTransitions": [{
        "NoncurrentDays": 30,
        "StorageClass": "GLACIER"
      }]
    }]
  }'
```

## Pattern 5: Database Connection Pooling

**Bad** - Default database connections:
```bash
# ❌ Default connections - bottleneck under load
POSTGRESQL_MAX_OPEN_CONNS=0
POSTGRESQL_MAX_IDLE_CONNS=2
```

**Good** - Optimized connection pool:
```bash
# ✅ Tuned connection pool for production
POSTGRESQL_HOST=postgres.example.com
POSTGRESQL_PORT=5432
POSTGRESQL_MAX_OPEN_CONNS=100
POSTGRESQL_MAX_IDLE_CONNS=50
POSTGRESQL_CONN_MAX_LIFETIME=5m
POSTGRESQL_SSLMODE=require

# Redis connection optimization
REDIS_HOST=redis.example.com:6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_DB_INDEX=0
REDIS_IDLE_TIMEOUT_SECONDS=30

# Monitor connection usage
psql -h postgres.example.com -U harbor -c \
  "SELECT count(*) as active_connections FROM pg_stat_activity WHERE datname='registry';"
```

## Pattern 6: Scan Performance Tuning

**Bad** - Sequential scanning with long timeout:
```bash
# ❌ Slow scanning blocks pushes
SCANNER_TRIVY_TIMEOUT=30m
# No parallelization
```

**Good** - Parallel scanning with optimized settings:
```bash
# ✅ Optimized Trivy scanner configuration
trivy:
  environment:
    SCANNER_TRIVY_TIMEOUT: "10m"
    SCANNER_TRIVY_VULN_TYPE: "os,library"
    SCANNER_TRIVY_SEVERITY: "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"
    SCANNER_TRIVY_SKIP_UPDATE: "false"
    SCANNER_TRIVY_GITHUB_TOKEN: "${GITHUB_TOKEN}"
    SCANNER_TRIVY_CACHE_DIR: "/home/scanner/.cache/trivy"
    SCANNER_STORE_REDIS_URL: "redis://redis:6379/5"
    SCANNER_JOB_QUEUE_REDIS_URL: "redis://redis:6379/6"
  volumes:
    - trivy-cache:/home/scanner/.cache/trivy
  deploy:
    replicas: 3
    resources:
      limits:
        memory: 4G
        cpus: '2'

# Pre-download vulnerability database
docker exec trivy trivy image --download-db-only
```
