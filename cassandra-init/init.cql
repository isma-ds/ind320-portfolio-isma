-- IND320 Assessment 4 - Cassandra Database Initialization
-- This script creates the keyspace and tables for energy data storage

-- Create keyspace with replication factor 3 (for 3-node cluster)
CREATE KEYSPACE IF NOT EXISTS ind320
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 3
};

-- Use the keyspace
USE ind320;

-- Table for 2021 consumption data
CREATE TABLE IF NOT EXISTS elhub_consumption_2021 (
    startTime timestamp,
    endTime timestamp,
    priceArea text,
    consumptionGroup text,
    quantityKwh double,
    meteringPointCount int,
    lastUpdatedTime timestamp,
    PRIMARY KEY ((priceArea, consumptionGroup), startTime)
) WITH CLUSTERING ORDER BY (startTime DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'}
  AND default_time_to_live = 0;

-- Table for 2022-2024 consumption data
CREATE TABLE IF NOT EXISTS elhub_consumption_2022_2024 (
    startTime timestamp,
    endTime timestamp,
    priceArea text,
    consumptionGroup text,
    quantityKwh double,
    meteringPointCount int,
    lastUpdatedTime timestamp,
    PRIMARY KEY ((priceArea, consumptionGroup), startTime)
) WITH CLUSTERING ORDER BY (startTime DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'}
  AND default_time_to_live = 0;

-- Table for 2022-2024 production data
CREATE TABLE IF NOT EXISTS elhub_production_2022_2024 (
    startTime timestamp,
    endTime timestamp,
    priceArea text,
    productionGroup text,
    quantityKwh double,
    lastUpdatedTime timestamp,
    PRIMARY KEY ((priceArea, productionGroup), startTime)
) WITH CLUSTERING ORDER BY (startTime DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'}
  AND default_time_to_live = 0;

-- Create secondary index on startTime for range queries
CREATE INDEX IF NOT EXISTS idx_consumption_2021_startTime
ON elhub_consumption_2021 (startTime);

CREATE INDEX IF NOT EXISTS idx_consumption_2022_2024_startTime
ON elhub_consumption_2022_2024 (startTime);

CREATE INDEX IF NOT EXISTS idx_production_2022_2024_startTime
ON elhub_production_2022_2024 (startTime);

-- Verify tables created
DESCRIBE TABLES;
