-- =============================================================================
-- NovaCRM — ClickHouse Seed Data
-- Time-series metrics and usage analytics
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. daily_active_users — 200 customers × 365 days ≈ 73K rows
-- Tracks DAU per customer with realistic growth/churn trends
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_active_users (
    customer_id UInt32,
    date Date,
    dau_count UInt32
) ENGINE = MergeTree()
ORDER BY (customer_id, date);

TRUNCATE TABLE IF EXISTS daily_active_users;

INSERT INTO daily_active_users
SELECT
    customer_id,
    date,
    -- Base DAU scaled by customer size, with trend and noise
    greatest(0, toUInt32(
        -- Base usage: 5-500 depending on customer bucket
        (5 + (customer_id * 7) % 496)
        -- Growth trend: +0.1% per day for growing customers, -0.3% for declining
        * (1.0 + (
            CASE
                WHEN customer_id % 7 < 2 THEN -0.003  -- declining (~30 customers)
                WHEN customer_id % 7 < 5 THEN 0.001   -- stable
                ELSE 0.002                              -- growing
            END
        ) * dateDiff('day', toDate('2024-01-01'), date))
        -- Weekly seasonality: lower on weekends
        + (CASE WHEN toDayOfWeek(date) IN (6, 7) THEN -15 ELSE 5 END)
        -- Random noise via hash
        + reinterpretAsInt16(substr(sipHash128(customer_id, date), 1, 2)) % 20
    ))
FROM (
    SELECT number + 1 AS customer_id
    FROM numbers(200)
) customers
CROSS JOIN (
    SELECT toDate('2024-01-01') + number AS date
    FROM numbers(365)
) dates;


-- ---------------------------------------------------------------------------
-- 2. api_usage_metrics — 200 customers × 365 days × 4 endpoints ≈ 292K rows
-- Tracks API call volume and latency per customer per endpoint
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS api_usage_metrics (
    customer_id UInt32,
    date Date,
    endpoint String,
    request_count UInt64,
    error_count UInt32,
    p50_latency_ms Float32,
    p99_latency_ms Float32
) ENGINE = MergeTree()
ORDER BY (customer_id, date, endpoint);

TRUNCATE TABLE IF EXISTS api_usage_metrics;

INSERT INTO api_usage_metrics
SELECT
    customer_id,
    date,
    endpoint,
    -- Request count: 10-10000 based on customer + endpoint mix
    greatest(1, toUInt64(
        (100 + (customer_id * 13 + cityHash64(endpoint)) % 9900)
        * (1.0 + 0.001 * dateDiff('day', toDate('2024-01-01'), date))
        + reinterpretAsInt16(substr(sipHash128(customer_id, date, endpoint), 1, 2)) % 200
    )) AS request_count,
    -- Error count: ~1-3% of requests, spikes for some customers
    toUInt32(greatest(0,
        greatest(1, toUInt64(
            (100 + (customer_id * 13 + cityHash64(endpoint)) % 9900)
            * (1.0 + 0.001 * dateDiff('day', toDate('2024-01-01'), date))
            + reinterpretAsInt16(substr(sipHash128(customer_id, date, endpoint), 1, 2)) % 200
        ))
        * (0.01 + 0.02 * (customer_id % 5 = 0))
        + reinterpretAsInt8(substr(sipHash128(customer_id, date, endpoint, 'err'), 1, 1)) % 5
    )) AS error_count,
    -- p50 latency: 15-80ms base
    greatest(5.0, toFloat32(
        25.0 + (cityHash64(endpoint) % 55)
        + reinterpretAsInt8(substr(sipHash128(customer_id, date, endpoint, 'p50'), 1, 1)) % 10
    )) AS p50_latency_ms,
    -- p99 latency: 3-8x of p50
    greatest(20.0, toFloat32(
        (25.0 + (cityHash64(endpoint) % 55)
         + reinterpretAsInt8(substr(sipHash128(customer_id, date, endpoint, 'p50'), 1, 1)) % 10)
        * (3.0 + (customer_id % 5))
        + reinterpretAsInt8(substr(sipHash128(customer_id, date, endpoint, 'p99'), 1, 1)) % 50
    )) AS p99_latency_ms
FROM (
    SELECT number + 1 AS customer_id FROM numbers(200)
) customers
CROSS JOIN (
    SELECT toDate('2024-01-01') + number AS date FROM numbers(365)
) dates
CROSS JOIN (
    SELECT arrayJoin(['/api/v2/contacts', '/api/v2/deals', '/api/v2/activities', '/api/v2/reports']) AS endpoint
) endpoints;


-- ---------------------------------------------------------------------------
-- 3. service_metrics — 4 services × 365 days × 24 hours ≈ 35K rows
-- Internal service health telemetry
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS service_metrics (
    service String,
    timestamp DateTime,
    error_rate Float32,
    request_count UInt32,
    cpu_percent Float32,
    memory_mb UInt32
) ENGINE = MergeTree()
ORDER BY (service, timestamp);

TRUNCATE TABLE IF EXISTS service_metrics;

INSERT INTO service_metrics
SELECT
    service,
    timestamp,
    -- Error rate: 0.1-2% base, occasional spikes to 5-15%
    greatest(0.0, toFloat32(
        0.005 + 0.005 * (cityHash64(service) % 3)
        + (CASE
            -- Inject incident spikes: ~2% of hours have elevated errors
            WHEN sipHash64(service, timestamp) % 50 = 0 THEN 0.05 + (sipHash64(service, timestamp, 'spike') % 10) * 0.01
            ELSE 0.0
           END)
        + reinterpretAsInt8(substr(sipHash128(service, timestamp, 'er'), 1, 1)) % 5 * 0.001
    )) AS error_rate,
    -- Request count: varies by service
    greatest(10, toUInt32(
        (CASE service
            WHEN 'api' THEN 50000
            WHEN 'web' THEN 30000
            WHEN 'worker' THEN 10000
            ELSE 5000  -- ml-pipeline
        END)
        -- Hour-of-day seasonality: peak at 14-16 UTC, trough at 4-6 UTC
        * (0.3 + 0.7 * ((1 + cos((toHour(timestamp) - 15) * 3.14159 / 12)) / 2))
        + reinterpretAsInt16(substr(sipHash128(service, timestamp, 'rc'), 1, 2)) % 2000
    )) AS request_count,
    -- CPU: 20-70% base with correlation to request count
    greatest(5.0, least(99.0, toFloat32(
        30.0 + 20.0 * (cityHash64(service) % 3)
        + 10.0 * ((1 + cos((toHour(timestamp) - 15) * 3.14159 / 12)) / 2)
        + reinterpretAsInt8(substr(sipHash128(service, timestamp, 'cpu'), 1, 1)) % 15
    ))) AS cpu_percent,
    -- Memory: 512-4096 MB depending on service
    toUInt32(greatest(256,
        (CASE service
            WHEN 'api' THEN 2048
            WHEN 'web' THEN 1024
            WHEN 'worker' THEN 1536
            ELSE 3072  -- ml-pipeline uses more memory
        END)
        + reinterpretAsInt16(substr(sipHash128(service, timestamp, 'mem'), 1, 2)) % 512
    )) AS memory_mb
FROM (
    SELECT arrayJoin(['api', 'web', 'worker', 'ml-pipeline']) AS service
) services
CROSS JOIN (
    SELECT toDateTime('2024-01-01 00:00:00') + (number * 3600) AS timestamp
    FROM numbers(365 * 24)
) hours;
