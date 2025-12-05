# RabbitMQ Clustering and High Availability Guide

## Overview

This guide covers RabbitMQ clustering, high availability patterns, quorum queues, federation, shovel, and strategies for handling network partitions.

---

## Quorum Queues for High Availability

### Overview

Quorum queues provide data replication and high availability using the Raft consensus algorithm. They are the recommended HA solution over classic mirrored queues.

### Basic Configuration

```python
# ✅ HA: Quorum queues with replication
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq-node-1')
)
channel = connection.channel()

# Declare quorum queue (replicated across cluster)
channel.queue_declare(
    queue='ha_tasks',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',  # Use quorum queue
        'x-max-in-memory-length': 0,  # All messages on disk
        'x-delivery-limit': 5  # Max delivery attempts
    }
)

# Quorum queues automatically handle:
# - Replication across cluster nodes
# - Leader election on node failure
# - Consistent message ordering
# - Poison message detection

# Publisher
channel.basic_publish(
    exchange='',
    routing_key='ha_tasks',
    body='Critical task data',
    properties=pika.BasicProperties(
        delivery_mode=2  # Persistent
    )
)
```

### Quorum Queue Benefits

- Data replication across nodes (consensus-based)
- Automatic failover without message loss
- Poison message detection with delivery limits
- Better consistency than classic mirrored queues

### Trade-offs

- Higher latency than classic queues
- More disk I/O (all messages persisted)
- Requires odd number of nodes (3, 5, 7)
- Higher memory usage per message

---

## Cluster Setup

### 3-Node Cluster Configuration

**Node 1 (rabbitmq1)**:
```bash
# /etc/rabbitmq/rabbitmq.conf
cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
cluster_formation.classic_config.nodes.1 = rabbit@rabbitmq1
cluster_formation.classic_config.nodes.2 = rabbit@rabbitmq2
cluster_formation.classic_config.nodes.3 = rabbit@rabbitmq3

# Erlang cookie (must be identical on all nodes)
echo "SAME_SECRET_COOKIE" > /var/lib/rabbitmq/.erlang.cookie
chmod 400 /var/lib/rabbitmq/.erlang.cookie
```

**Node 2 and 3**: Same configuration with node names

### Joining Cluster

```bash
# On node 2 and 3
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl join_cluster rabbit@rabbitmq1
rabbitmqctl start_app

# Verify cluster status
rabbitmqctl cluster_status
```

### Cluster Status Check

```bash
# Check cluster status
rabbitmqctl cluster_status

# Expected output:
# Cluster status of node rabbit@rabbitmq1
# Basics
# Cluster name: production-cluster
# Disk Nodes: rabbit@rabbitmq1, rabbit@rabbitmq2, rabbit@rabbitmq3
# Running Nodes: rabbit@rabbitmq1, rabbit@rabbitmq2, rabbit@rabbitmq3
```

---

## Network Partition Handling

### Partition Modes

RabbitMQ provides several strategies for handling network partitions:

#### 1. Autoheal (Recommended for Most Cases)

```ini
# /etc/rabbitmq/rabbitmq.conf
cluster_partition_handling = autoheal
```

**Behavior**:
- Automatically heals partitions
- Chooses "winner" partition with most clients
- Restarts losing nodes

**Use When**:
- You want automatic recovery
- Temporary message loss is acceptable
- Client reconnection is implemented

#### 2. Pause Minority

```ini
cluster_partition_handling = pause_minority
```

**Behavior**:
- Pauses minority partition nodes
- Maintains data consistency
- Requires manual intervention

**Use When**:
- Data consistency is critical
- You have operational staff to handle partitions
- You prefer no data loss over availability

#### 3. Ignore (Not Recommended)

```ini
cluster_partition_handling = ignore
```

**Behavior**:
- Does nothing
- Manual intervention required
- Data divergence possible

**Use When**:
- You have custom partition handling
- Testing/development only

### Monitoring Partitions

```python
# Check for partitions via management API
import requests

response = requests.get(
    'http://localhost:15672/api/nodes',
    auth=('admin', 'password')
)

for node in response.json():
    if node.get('partitions'):
        print(f"Partition detected on {node['name']}: {node['partitions']}")
```

---

## Federation

### Overview

Federation allows connecting RabbitMQ brokers across different networks, data centers, or administrative domains without clustering.

### Use Cases

- Geographically distributed systems
- WAN connections (unreliable networks)
- Different administrative domains
- One-way message flow needed

### Federation Setup

**Upstream Configuration** (source broker):
```bash
# Define upstream
rabbitmqctl set_parameter federation-upstream my-upstream \
  '{"uri":"amqp://user:pass@remote-broker:5672","ack-mode":"on-confirm"}'

# Create federation policy
rabbitmqctl set_policy federate-me \
  "^federated\." \
  '{"federation-upstream-set":"all"}' \
  --priority 10 \
  --apply-to exchanges
```

**Downstream Configuration** (receiving broker):
```python
# Create exchange on downstream
channel.exchange_declare(
    exchange='federated.orders',
    exchange_type='topic',
    durable=True
)

# Bind queue
channel.queue_declare(queue='local_orders', durable=True)
channel.queue_bind(
    exchange='federated.orders',
    queue='local_orders',
    routing_key='order.#'
)
```

### Federation Patterns

#### Pattern 1: Upstream Federation (Pull)

Messages flow from upstream to downstream:
- Downstream pulls messages from upstream
- Multiple downstreams can pull from one upstream
- Suitable for fan-out scenarios

#### Pattern 2: Bidirectional Federation

Both brokers act as upstream and downstream:
```bash
# On broker A
rabbitmqctl set_parameter federation-upstream broker-b \
  '{"uri":"amqp://broker-b:5672"}'

# On broker B
rabbitmqctl set_parameter federation-upstream broker-a \
  '{"uri":"amqp://broker-a:5672"}'
```

---

## Shovel

### Overview

Shovel provides reliable message transfer between brokers or queues. Unlike federation, it's queue-centric rather than exchange-centric.

### Use Cases

- Migrating messages between clusters
- Copying messages for analytics
- One-time data movement
- Different protocols (AMQP to other)

### Shovel Configuration

#### Static Shovel

```bash
# Define shovel
rabbitmqctl set_parameter shovel my-shovel \
  '{"src-protocol": "amqp091",
    "src-uri": "amqp://localhost",
    "src-queue": "source-queue",
    "dest-protocol": "amqp091",
    "dest-uri": "amqp://remote-host",
    "dest-queue": "destination-queue",
    "ack-mode": "on-confirm"}'
```

#### Dynamic Shovel via Management API

```python
import requests

shovel_config = {
    "value": {
        "src-protocol": "amqp091",
        "src-uri": "amqp://localhost",
        "src-queue": "source",
        "dest-protocol": "amqp091",
        "dest-uri": "amqp://remote:5672",
        "dest-queue": "destination",
        "ack-mode": "on-confirm",
        "reconnect-delay": 5
    }
}

requests.put(
    'http://localhost:15672/api/parameters/shovel/%2f/my-shovel',
    json=shovel_config,
    auth=('admin', 'password')
)
```

### Shovel Acknowledgment Modes

- `on-confirm`: Ack source after destination confirms (safest)
- `on-publish`: Ack source immediately after publish
- `no-ack`: Auto-ack (fastest, least safe)

---

## Load Balancing

### HAProxy Configuration

```haproxy
# /etc/haproxy/haproxy.cfg
global
    log /dev/log local0
    maxconn 4096

defaults
    log global
    mode tcp
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

# AMQP Load Balancer
listen rabbitmq_amqp
    bind *:5672
    mode tcp
    balance roundrobin
    server rabbitmq1 10.0.0.1:5672 check inter 5s
    server rabbitmq2 10.0.0.2:5672 check inter 5s
    server rabbitmq3 10.0.0.3:5672 check inter 5s

# Management UI
listen rabbitmq_mgmt
    bind *:15672
    mode http
    balance roundrobin
    server rabbitmq1 10.0.0.1:15672 check inter 5s
    server rabbitmq2 10.0.0.2:15672 check inter 5s
    server rabbitmq3 10.0.0.3:15672 check inter 5s
```

### Client-Side Load Balancing

```python
import pika
import random

class LoadBalancedConnection:
    def __init__(self, hosts):
        self.hosts = hosts

    def connect(self):
        # Shuffle for random distribution
        hosts = self.hosts.copy()
        random.shuffle(hosts)

        for host in hosts:
            try:
                return pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=host,
                        connection_attempts=3,
                        retry_delay=2
                    )
                )
            except pika.exceptions.AMQPConnectionError:
                continue

        raise Exception("All RabbitMQ nodes unavailable")

# Usage
lb = LoadBalancedConnection(['rabbitmq1', 'rabbitmq2', 'rabbitmq3'])
connection = lb.connect()
```

---

## Cluster Monitoring

### Key Cluster Metrics

1. **Node Health**
   - Node status (running/stopped)
   - Disk/memory alarms
   - File descriptor usage

2. **Cluster Connectivity**
   - Inter-node communication
   - Network partitions
   - Erlang distribution port

3. **Queue Distribution**
   - Queue master locations
   - Replica synchronization status
   - Message distribution

### Prometheus Queries

```promql
# Check for network partitions
rabbitmq_identity_info{partition="yes"} > 0

# Node memory usage
rabbitmq_node_mem_used / rabbitmq_node_mem_limit > 0.8

# Queue synchronization lag
rabbitmq_queue_messages_unacked > 1000

# Cluster-wide message rate
sum(rate(rabbitmq_queue_messages_published_total[5m]))
```

### Health Check Script

```python
import requests
import sys

def check_cluster_health(mgmt_url, username, password):
    """Check RabbitMQ cluster health"""
    issues = []

    # Check nodes
    nodes_response = requests.get(
        f'{mgmt_url}/api/nodes',
        auth=(username, password)
    )

    for node in nodes_response.json():
        if not node['running']:
            issues.append(f"Node {node['name']} is not running")

        if node.get('mem_alarm'):
            issues.append(f"Memory alarm on {node['name']}")

        if node.get('disk_free_alarm'):
            issues.append(f"Disk alarm on {node['name']}")

        if node.get('partitions'):
            issues.append(f"Network partition on {node['name']}")

    # Check quorum queues
    queues_response = requests.get(
        f'{mgmt_url}/api/queues',
        auth=(username, password)
    )

    for queue in queues_response.json():
        if queue.get('type') == 'quorum':
            if queue.get('state') != 'running':
                issues.append(f"Quorum queue {queue['name']} not running")

    if issues:
        print("❌ Cluster health issues:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ Cluster healthy")
        sys.exit(0)

# Usage
check_cluster_health('http://localhost:15672', 'admin', 'password')
```

---

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# Backup RabbitMQ definitions

BACKUP_DIR="/backup/rabbitmq/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Export definitions (exchanges, queues, bindings, users)
curl -u admin:password \
  http://localhost:15672/api/definitions \
  -o "$BACKUP_DIR/definitions.json"

# Backup Erlang cookie
cp /var/lib/rabbitmq/.erlang.cookie "$BACKUP_DIR/"

# Backup configuration
cp /etc/rabbitmq/rabbitmq.conf "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

### Restore Strategy

```bash
#!/bin/bash
# Restore RabbitMQ definitions

BACKUP_FILE="$1"

# Import definitions
curl -u admin:password \
  -H "Content-Type: application/json" \
  -X POST \
  http://localhost:15672/api/definitions \
  -d @"$BACKUP_FILE"

echo "Restore completed from: $BACKUP_FILE"
```

### Blue-Green Deployment

```bash
# Step 1: Setup new cluster (green)
# Step 2: Setup shovel from old (blue) to new (green)
rabbitmqctl set_parameter shovel migration-shovel \
  '{"src-uri": "amqp://blue-cluster",
    "src-queue": "queue-name",
    "dest-uri": "amqp://green-cluster",
    "dest-queue": "queue-name"}'

# Step 3: Redirect publishers to green cluster
# Step 4: Wait for shovel to drain blue cluster
# Step 5: Redirect consumers to green cluster
# Step 6: Decommission blue cluster
```

---

## Cluster Sizing Recommendations

### Small Cluster (< 1000 msg/s)

- **Nodes**: 3
- **Instance Type**: 2 vCPU, 4GB RAM
- **Storage**: 50GB SSD
- **Use Case**: Development, small production

### Medium Cluster (1000-10000 msg/s)

- **Nodes**: 3-5
- **Instance Type**: 4 vCPU, 8GB RAM
- **Storage**: 100GB SSD
- **Use Case**: Production workloads

### Large Cluster (> 10000 msg/s)

- **Nodes**: 5-7
- **Instance Type**: 8+ vCPU, 16GB+ RAM
- **Storage**: 500GB+ NVMe SSD
- **Use Case**: High-throughput production

### Anti-Patterns

❌ **Don't**:
- Use even number of nodes (causes split-brain)
- Run single-node in production
- Use classic mirrored queues (deprecated)
- Mix disk and RAM nodes without understanding trade-offs

✅ **Do**:
- Use odd number of nodes (3, 5, 7)
- Use quorum queues for HA
- Monitor cluster health continuously
- Test partition handling scenarios
- Document failover procedures

---

## Cluster Checklist

Before going to production:

- [ ] Odd number of nodes (3, 5, or 7)
- [ ] Quorum queues for critical workloads
- [ ] Partition handling strategy configured
- [ ] Load balancer configured (HAProxy/NGINX)
- [ ] Monitoring and alerting enabled
- [ ] Backup and restore procedures tested
- [ ] Disaster recovery plan documented
- [ ] Network partition testing completed
- [ ] Failover procedures validated
- [ ] Client retry logic implemented
