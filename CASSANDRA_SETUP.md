# Cassandra Setup Guide - IND320 Assessment 4

## Overview

This guide explains how to set up and use the local Cassandra database cluster for storing real Elhub energy data.

## Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available for Docker
- Python 3.12+ with cassandra-driver package
- Real or synthetic energy data in CSV format

## Quick Start

### 1. Start Cassandra Cluster

```bash
# Windows
cassandra_manager.bat start

# Or using Docker Compose directly
docker-compose up -d
```

This starts a 3-node Cassandra cluster:
- **Node 1**: localhost:9042 (CQL port)
- **Node 2**: localhost:9043
- **Node 3**: localhost:9044

### 2. Wait for Cluster Initialization

The cluster takes 2-3 minutes to fully initialize. Check status:

```bash
cassandra_manager.bat status
```

All nodes should show status "Up" before proceeding.

### 3. Initialize Database Schema

```bash
cassandra_manager.bat init
```

This creates:
- Keyspace: `ind320` (replication factor 3)
- Tables:
  - `elhub_consumption_2021`
  - `elhub_consumption_2022_2024`
  - `elhub_production_2022_2024`

### 4. Upload Data

```bash
cassandra_manager.bat upload
```

This uploads CSV files from the `data/` directory to Cassandra.

### 5. Verify Data

Access the CQL shell:

```bash
cassandra_manager.bat shell
```

Run verification queries:

```sql
USE ind320;

-- Check table row counts
SELECT COUNT(*) FROM elhub_consumption_2021;
SELECT COUNT(*) FROM elhub_consumption_2022_2024;
SELECT COUNT(*) FROM elhub_production_2022_2024;

-- Sample data
SELECT * FROM elhub_consumption_2021 LIMIT 10;
```

## Architecture

### Cluster Configuration

- **Cluster Name**: IND320_Cluster
- **Replication Strategy**: SimpleStrategy
- **Replication Factor**: 3
- **Nodes**: 3 (cassandra1, cassandra2, cassandra3)
- **Data Center**: datacenter1

### Table Schema

**elhub_consumption_2021** and **elhub_consumption_2022_2024**:
```sql
CREATE TABLE elhub_consumption_YYYY (
    startTime timestamp,
    endTime timestamp,
    priceArea text,
    consumptionGroup text,
    quantityKwh double,
    meteringPointCount int,
    lastUpdatedTime timestamp,
    PRIMARY KEY ((priceArea, consumptionGroup), startTime)
) WITH CLUSTERING ORDER BY (startTime DESC);
```

**elhub_production_2022_2024**:
```sql
CREATE TABLE elhub_production_2022_2024 (
    startTime timestamp,
    endTime timestamp,
    priceArea text,
    productionGroup text,
    quantityKwh double,
    lastUpdatedTime timestamp,
    PRIMARY KEY ((priceArea, productionGroup), startTime)
) WITH CLUSTERING ORDER BY (startTime DESC);
```

### Partition Key Design

- **Partition Key**: (priceArea, consumptionGroup) or (priceArea, productionGroup)
  - Ensures even distribution across nodes
  - Groups related data together
  - Efficient for price area queries

- **Clustering Key**: startTime (descending)
  - Enables fast time-range queries
  - Latest data retrieved first

## Using Cassandra in Streamlit

The application provides a Cassandra client (`cassandra_client.py`) that mirrors the MongoDB interface.

### Import the Client

```python
import cassandra_client as cass

# Get session
session = cass.get_cassandra_session()

# Check connection
status = cass.check_connection()
st.write(status)

# Fetch data
df = cass.fetch_consumption_data(
    collection_name='elhub_consumption_2021',
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 12, 31)
)
```

### Available Functions

- `get_cassandra_session()`: Get cached session
- `check_connection()`: Verify connectivity
- `fetch_consumption_data()`: Query consumption tables
- `fetch_production_data()`: Query production tables
- `get_available_groups()`: List consumption/production groups
- `get_available_price_areas()`: List price areas
- `get_collection_count()`: Count table rows

## Management Commands

### Start Cluster
```bash
cassandra_manager.bat start
```

### Stop Cluster
```bash
cassandra_manager.bat stop
```

### Check Status
```bash
cassandra_manager.bat status
```

### View Logs
```bash
# All nodes
cassandra_manager.bat logs

# Specific node
cassandra_manager.bat logs cassandra1
```

### Access CQL Shell
```bash
cassandra_manager.bat shell
```

### Remove All Data (WARNING: Destructive)
```bash
cassandra_manager.bat clean
```

## Troubleshooting

### Cluster Won't Start

1. Check Docker is running: `docker ps`
2. Check available RAM: Docker needs 4GB minimum
3. View logs: `cassandra_manager.bat logs`
4. Restart Docker Desktop

### Connection Refused

- Cluster may still be initializing (wait 2-3 minutes)
- Check node health: `docker exec cassandra1 nodetool status`
- Verify port 9042 is not in use: `netstat -an | findstr 9042`

### Slow Queries

- Cassandra is optimized for partition key queries
- Avoid `ALLOW FILTERING` in production
- Use appropriate WHERE clauses with partition keys
- Consider adding secondary indexes for common queries

### Out of Memory

- Reduce heap size in docker-compose.yml:
  ```yaml
  MAX_HEAP_SIZE=512M
  HEAP_NEWSIZE=100M
  ```
- Run fewer nodes (comment out cassandra2/cassandra3)
- Adjust Docker Desktop memory allocation

## Data Volume

Estimated storage for Assessment 4:

- 2021 Consumption: ~175,200 records → ~50 MB
- 2022-2024 Consumption: ~526,080 records → ~150 MB
- 2022-2024 Production: ~526,080 records → ~150 MB
- **Total**: ~1.4M records, ~350 MB raw data
- **With Replication (×3)**: ~1 GB total

## Performance Optimization

### Batch Uploads

The upload script uses batch statements (100 records per batch) for optimal performance:

```python
batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
for row in data:
    batch.add(insert_stmt, row)
session.execute(batch)
```

### Query Optimization

1. **Always use partition key** in WHERE clause
2. **Limit time ranges** for large datasets
3. **Use caching** (@st.cache_data) in Streamlit
4. **Avoid COUNT(*)** on large tables (use estimates)

### Consistency Levels

- **QUORUM**: Default for writes (2/3 nodes)
- **ONE**: Faster, less consistent
- **ALL**: Slowest, most consistent

## Comparison: MongoDB vs Cassandra

| Feature | MongoDB | Cassandra |
|---------|---------|-----------|
| **Data Model** | Document (JSON) | Wide-column (tables) |
| **Query Language** | MongoDB Query API | CQL (SQL-like) |
| **Replication** | Replica sets | Multi-datacenter |
| **Scaling** | Vertical + Horizontal | Horizontal (linear) |
| **Consistency** | Strong by default | Tunable (eventual) |
| **Best For** | Complex queries | Time-series, high writes |
| **Deployment** | Cloud (Atlas) | Local (Docker) |

## Next Steps

1. Fetch real Elhub data: `python scripts/fetch_elhub_data.py`
2. Upload to Cassandra: `python scripts/upload_to_cassandra.py`
3. Update Streamlit pages to use `cassandra_client.py`
4. Test application with real data
5. Deploy Streamlit app with Cassandra backend

## References

- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [DataStax Python Driver](https://docs.datastax.com/en/developer/python-driver/)
- [CQL Reference](https://cassandra.apache.org/doc/latest/cassandra/cql/)
- [Docker Compose](https://docs.docker.com/compose/)

---

**Assessment 4 - IND320**
**Date**: 2025-11-17
**Database**: Apache Cassandra 4.1
