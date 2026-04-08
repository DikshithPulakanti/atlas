"""Seed Weaviate with NovaCRM knowledge and incident data.

Creates two collections:
  - IncidentReport: 150 SaaS incident summaries for semantic similarity search
  - KnowledgeArticle: 200 internal how-to articles and best practices

Idempotent: deletes and recreates collections on each run.
"""

import sys
import time
import random
from datetime import datetime, timedelta

import requests
import weaviate
from faker import Faker

WEAVIATE_URL = "http://localhost:8080"
fake = Faker()
Faker.seed(42)
random.seed(42)


def wait_for_weaviate(timeout: int = 60) -> None:
    """Block until Weaviate is healthy."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{WEAVIATE_URL}/v1/.well-known/ready", timeout=5)
            if r.ok:
                print("Weaviate is healthy.")
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    print("ERROR: Weaviate not ready after timeout.", file=sys.stderr)
    sys.exit(1)


def delete_collection_if_exists(client: weaviate.Client, name: str) -> None:
    """Remove a collection if it already exists."""
    if client.collections.exists(name):
        client.collections.delete(name)
        print(f"  Deleted existing collection '{name}'.")


# =============================================================================
# 1. IncidentReport — 150 SaaS incident summaries
# =============================================================================

INCIDENT_TITLES = [
    "API gateway returning 502 errors for US-East region",
    "Database primary failover triggered during peak hours",
    "Elasticsearch cluster went red — search unavailable for 23 minutes",
    "Authentication service latency spike causing login failures",
    "Billing webhook processor stuck — invoices delayed 4 hours",
    "CDN cache poisoning serving stale JavaScript bundles",
    "Redis sentinel failover loop causing intermittent cache misses",
    "Worker queue backlog exceeded 500K — async jobs delayed",
    "SSL certificate auto-renewal failed — mixed content warnings",
    "Data pipeline lag — customer analytics dashboards 6 hours behind",
    "Memory leak in notification service — OOM kills every 12 hours",
    "DNS propagation delay after provider migration — partial outage",
    "Rate limiter misconfiguration — enterprise customers throttled at free tier limits",
    "Database connection pool exhaustion during batch import",
    "Kafka consumer group rebalance storm — event processing halted",
    "Storage volume at 95% capacity — write operations failing",
    "GraphQL resolver timeout cascade — dashboard completely unresponsive",
    "Deployment rollback failed — config drift between environments",
    "Third-party email provider outage — transactional emails queued",
    "Search index rebuild corrupted — partial results for 2 hours",
]

ROOT_CAUSES = [
    "Configuration change deployed without canary rollout",
    "Upstream dependency timeout not properly configured",
    "Missing database index caused full table scan under load",
    "Memory leak introduced in v2.14.3 release",
    "Network partition between availability zones",
    "Certificate rotation cron job silently failing for 3 weeks",
    "Connection pool size insufficient for traffic pattern change",
    "Kafka partition rebalance triggered by broker rolling restart",
    "Disk I/O contention from competing batch workloads",
    "Race condition in distributed lock implementation",
]

RESOLUTIONS = [
    "Rolled back to previous version and applied hotfix",
    "Increased connection pool size and added circuit breaker",
    "Added missing database index and optimized query plan",
    "Restarted affected pods and patched memory leak",
    "Failed over to secondary region and fixed network config",
    "Manually renewed certificate and fixed automation",
    "Scaled up worker fleet and drained backlog",
    "Reconfigured rate limiter with correct tier mappings",
    "Cleared corrupted cache entries and forced rebuild",
    "Applied emergency config change and added monitoring",
]

SERVICES_POOL = ["api", "web", "worker", "ml-pipeline", "auth", "billing",
                 "search", "notifications", "analytics", "data-pipeline"]

INCIDENT_SUMMARIES = [
    (
        "At {time} UTC on {date}, the API gateway began returning 502 Bad Gateway errors "
        "for approximately {pct}% of requests in the US-East region. The issue was caused by "
        "a health check misconfiguration that marked all backend pods as unhealthy after a "
        "routine Kubernetes node upgrade. The load balancer drained connections from the "
        "affected pods, leaving no healthy backends to serve traffic. The incident affected "
        "{customers} enterprise customers and resulted in approximately {errors:,} failed API "
        "calls over the {duration}-minute incident window. The on-call engineer identified the "
        "root cause by examining the ingress controller logs and corrected the health check "
        "endpoint configuration. A post-incident review revealed that the health check path "
        "had been changed in a recent refactor but the ingress annotations were not updated."
    ),
    (
        "The primary PostgreSQL database triggered an automatic failover at {time} UTC on "
        "{date} due to a replication lag exceeding the configured threshold of 30 seconds. "
        "The lag was caused by a long-running analytical query from the reporting service "
        "that acquired row-level locks on the customers table. During the {duration}-minute "
        "failover, write operations returned errors and read operations experienced elevated "
        "latency. {customers} customers reported issues with saving deals and updating contacts. "
        "The situation was exacerbated by the connection pool not properly draining connections "
        "to the old primary, causing a thundering herd when clients reconnected to the new "
        "primary. Resolution involved killing the offending query, verifying replication "
        "health, and tuning the failover threshold."
    ),
    (
        "Starting at {time} UTC on {date}, our Elasticsearch cluster entered a red state after "
        "the data-3 node experienced a JVM heap exhaustion. The node was processing an unusually "
        "large bulk indexing request from the data pipeline service, which attempted to index "
        "{errors:,} documents in a single batch. With one data node down, several primary shards "
        "became unassigned, causing search queries to return partial or empty results. The incident "
        "lasted {duration} minutes and impacted search functionality for all customers. "
        "Recovery involved restarting the failed node, waiting for shard recovery, and implementing "
        "a bulk indexing size limit of 5,000 documents per batch."
    ),
    (
        "On {date}, the authentication service experienced a latency spike beginning at {time} UTC, "
        "with p99 response times increasing from 200ms to over 8 seconds. The spike was caused by "
        "an expired TLS certificate on the connection between the auth service and the session "
        "store (Redis). The auth service fell back to synchronous database lookups for session "
        "validation, overwhelming the database connection pool. Approximately {pct}% of login "
        "attempts failed during the {duration}-minute incident. {customers} customers opened "
        "support tickets. The certificate was renewed manually, and we added monitoring for "
        "certificate expiration dates across all internal services."
    ),
    (
        "A memory leak in the notification service was identified on {date} after the service "
        "experienced its third OOM kill in 48 hours. Each restart cycle lasted approximately "
        "{duration} minutes, during which queued notifications (email, in-app, webhook) were "
        "delayed. The leak was traced to an event listener that accumulated references to "
        "closed WebSocket connections. Over a 12-hour period, the service's heap usage grew "
        "from 512MB to 4GB before hitting the container memory limit. The fix involved "
        "properly deregistering event listeners on connection close. Approximately {errors:,} "
        "notifications were delayed by an average of 45 minutes during the affected period."
    ),
    (
        "The worker queue service experienced a severe backlog on {date}, growing to over "
        "500,000 pending jobs by {time} UTC. The root cause was a deadlock in the job "
        "scheduler introduced by a concurrent retry mechanism added in the previous release. "
        "When two workers attempted to retry the same failed job simultaneously, they acquired "
        "locks in opposite order, causing both to hang indefinitely. Over {duration} minutes, "
        "the backlog caused delays in background data sync, report generation, and webhook "
        "delivery for {customers} customers. Resolution required a rolling restart of all "
        "worker pods and a code fix to enforce consistent lock ordering."
    ),
    (
        "On {date} at {time} UTC, the billing service began generating incorrect invoices "
        "for customers on annual plans. A timezone handling bug in the proration calculator "
        "caused mid-cycle plan changes to be calculated using UTC dates instead of the "
        "customer's billing timezone. This resulted in {customers} customers receiving invoices "
        "with incorrect amounts, ranging from underbilling of $50 to overbilling of $2,300. "
        "The issue persisted for {duration} minutes before being detected by an automated "
        "billing anomaly alert. All affected invoices were voided and recalculated, and "
        "customers were notified with apologies. Total financial impact: ${errors:,} in "
        "billing adjustments."
    ),
    (
        "A Kafka consumer group rebalance storm occurred on {date}, triggered by a broker "
        "configuration change during a routine maintenance window. The rebalance caused all "
        "consumers in the event-processing group to repeatedly join and leave the group, "
        "preventing any meaningful event processing for {duration} minutes. During this period, "
        "approximately {errors:,} events accumulated in the topic backlog. The issue affected "
        "real-time features including activity feeds, live dashboards, and webhook deliveries. "
        "The incident was resolved by reverting the broker configuration and performing a "
        "controlled rolling restart. We subsequently implemented consumer group stability "
        "monitoring and increased the session.timeout.ms to reduce rebalance sensitivity."
    ),
]


def seed_incident_reports(client: weaviate.Client) -> None:
    """Create and populate the IncidentReport collection."""
    delete_collection_if_exists(client, "IncidentReport")

    client.collections.create(
        name="IncidentReport",
        properties=[
            weaviate.classes.config.Property(name="title", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="summary", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="severity", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="root_cause", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="resolution", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="duration_minutes", data_type=weaviate.classes.config.DataType.INT),
            weaviate.classes.config.Property(name="services_affected", data_type=weaviate.classes.config.DataType.TEXT_ARRAY),
            weaviate.classes.config.Property(name="created_at", data_type=weaviate.classes.config.DataType.DATE),
        ],
    )
    print("  Created collection 'IncidentReport'.")

    collection = client.collections.get("IncidentReport")
    severities = ["low", "medium", "high", "critical"]

    with collection.batch.dynamic() as batch:
        for i in range(150):
            duration = random.choice([5, 12, 23, 35, 45, 60, 90, 120])
            created = fake.date_time_between(start_date="-2y", end_date="now")
            vals = {
                "time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
                "date": created.strftime("%Y-%m-%d"),
                "pct": random.randint(10, 80),
                "customers": random.randint(5, 200),
                "errors": random.randint(500, 50000),
                "duration": duration,
            }

            batch.add_object(properties={
                "title": INCIDENT_TITLES[i % len(INCIDENT_TITLES)],
                "summary": INCIDENT_SUMMARIES[i % len(INCIDENT_SUMMARIES)].format(**vals),
                "severity": random.choice(severities),
                "root_cause": ROOT_CAUSES[i % len(ROOT_CAUSES)],
                "resolution": RESOLUTIONS[i % len(RESOLUTIONS)],
                "duration_minutes": duration,
                "services_affected": random.sample(SERVICES_POOL, k=random.randint(1, 4)),
                "created_at": created.isoformat() + "Z",
            })

    print(f"  Inserted 150 IncidentReport objects.")


# =============================================================================
# 2. KnowledgeArticle — 200 how-to articles and best practices
# =============================================================================

KB_CATEGORIES = ["how-to", "best-practices", "troubleshooting", "architecture",
                 "onboarding", "security", "performance", "integrations"]

KB_TITLES = [
    "How to configure SSO with Okta for NovaCRM",
    "Best practices for API key management and rotation",
    "Troubleshooting slow dashboard load times",
    "Architecture guide: understanding the data pipeline",
    "Getting started: importing contacts from CSV",
    "Security hardening checklist for enterprise deployments",
    "Performance tuning guide for high-volume API usage",
    "Integrating NovaCRM with Slack for real-time notifications",
    "How to set up custom webhooks for deal stage changes",
    "Best practices for organizing teams and permissions",
    "Troubleshooting email delivery issues",
    "Architecture guide: multi-region deployment",
    "Getting started: building your first sales pipeline",
    "Security guide: enabling two-factor authentication",
    "Performance guide: optimizing bulk data imports",
    "Integrating with Zapier for workflow automation",
    "How to create custom reports and dashboards",
    "Best practices for data backup and disaster recovery",
    "Troubleshooting API rate limit errors",
    "Architecture guide: event-driven integrations with webhooks",
]

KB_CONTENTS = [
    (
        "This guide walks you through configuring SAML-based Single Sign-On (SSO) between "
        "Okta and NovaCRM. Prerequisites: Admin access to both Okta and NovaCRM, an enterprise "
        "plan subscription. Step 1: In Okta, navigate to Applications > Add Application and "
        "search for NovaCRM in the catalog. If not found, create a custom SAML 2.0 application. "
        "Step 2: Configure the SSO URL as https://app.novacrm.io/auth/saml/callback and the "
        "Audience URI as https://app.novacrm.io. Step 3: Download the IdP metadata XML from "
        "Okta. Step 4: In NovaCRM, go to Settings > Security > SSO and upload the metadata. "
        "Step 5: Map the Okta attributes (email, firstName, lastName) to NovaCRM fields. "
        "Step 6: Test with a single user before enabling for the entire organization. Common "
        "pitfalls: ensure the Name ID format is set to emailAddress, and that the ACS URL "
        "exactly matches including the trailing slash."
    ),
    (
        "API keys are the primary authentication mechanism for programmatic access to NovaCRM. "
        "Follow these best practices: 1) Never embed API keys in client-side code or public "
        "repositories. Use environment variables or a secrets manager. 2) Create separate API "
        "keys for each integration and label them descriptively (e.g., 'salesforce-sync-prod'). "
        "3) Rotate keys every 90 days. NovaCRM supports key rotation without downtime — create "
        "the new key, update your integration, then revoke the old key. 4) Use the principle of "
        "least privilege — assign only the scopes your integration needs. For read-only sync, "
        "use the 'contacts:read' and 'deals:read' scopes. 5) Monitor API key usage in "
        "Settings > API > Usage Logs. Set up alerts for unusual patterns like sudden spikes or "
        "requests from unexpected IP ranges. 6) For enterprise customers, consider using OAuth 2.0 "
        "with client credentials grant instead of static API keys for server-to-server integrations."
    ),
    (
        "If your NovaCRM dashboard is loading slowly, follow this troubleshooting guide. "
        "First, check your browser's Developer Tools > Network tab for slow requests. Common "
        "culprits: 1) The /api/v2/deals endpoint takes >5s: This usually indicates too many "
        "deals in your pipeline. Enable pagination in Settings > Display > Default Page Size "
        "and reduce from the default 100 to 25. 2) The /api/v2/reports/pipeline endpoint is "
        "slow: This runs a complex aggregation query. Check if you have custom fields with "
        "formula calculations — each formula adds latency. Simplify or remove unused formulas. "
        "3) Multiple API calls fire sequentially: If you have many dashboard widgets, each "
        "fires its own API call. Contact support to enable the beta 'batched dashboard API' "
        "which consolidates these into a single request. 4) Browser extensions interfering: "
        "Test in an incognito window with all extensions disabled. Ad blockers sometimes "
        "interfere with our analytics scripts, causing retry loops."
    ),
    (
        "NovaCRM's data pipeline processes events in real-time using a Kafka-based event streaming "
        "architecture. Here's how it works: 1) User actions (create contact, update deal, etc.) "
        "generate events that are published to Kafka topics. 2) The event processor service "
        "consumes these events and routes them to the appropriate handlers: search indexing, "
        "analytics aggregation, webhook delivery, and notification dispatch. 3) The analytics "
        "service aggregates events into time-series metrics stored in ClickHouse, which powers "
        "the reporting dashboards. 4) The search indexer updates the Elasticsearch indices in "
        "near real-time (typical lag: <500ms). 5) Webhooks are delivered asynchronously with "
        "at-least-once semantics — your endpoint may receive duplicate events, so implement "
        "idempotency using the event_id field. The pipeline processes approximately 50 million "
        "events per day with a p99 end-to-end latency of 2 seconds."
    ),
    (
        "This security hardening checklist covers the essential configurations for enterprise "
        "NovaCRM deployments. Authentication: Enable SSO via SAML 2.0 or OIDC. Enforce MFA for "
        "all admin accounts. Set session timeout to 8 hours maximum. Disable password-based "
        "authentication once SSO is configured. Network: Restrict API access by IP whitelist "
        "(Settings > Security > IP Restrictions). Enable TLS 1.3 for all API connections. "
        "Data: Enable field-level encryption for sensitive data (SSN, credit card). Configure "
        "data retention policies to auto-delete records after your compliance period. Audit: "
        "Enable comprehensive audit logging (Settings > Security > Audit Trail). Export logs "
        "to your SIEM via our syslog integration. Set up alerts for: admin role changes, bulk "
        "data exports >10,000 records, API key creation, and failed login attempts >5 in 10 "
        "minutes. Compliance: Request your SOC 2 Type II report from your account manager. "
        "Enable HIPAA mode if handling healthcare data."
    ),
    (
        "For high-volume API users (>100K requests/day), follow these performance optimization "
        "guidelines. Batch operations: Use the /api/v2/batch endpoint to group up to 100 "
        "create/update operations in a single request. This reduces HTTP overhead by 90% and "
        "is processed as a single transaction. Pagination: Always use cursor-based pagination "
        "(after parameter) instead of offset-based. Offset pagination degrades at high page "
        "numbers. Field selection: Use the fields query parameter to request only the columns "
        "you need. Requesting all fields for contacts with 50+ custom fields adds significant "
        "serialization overhead. Caching: Implement conditional requests with If-None-Match "
        "headers. Our API returns ETag headers that you can use to skip downloading unchanged "
        "data. Connection pooling: Reuse HTTP connections. Our API supports HTTP/2 multiplexing "
        "which allows concurrent requests over a single TCP connection. Rate limit awareness: "
        "Implement exponential backoff when you receive 429 responses. Check X-RateLimit-Reset "
        "to calculate the optimal retry time."
    ),
    (
        "Integrate NovaCRM with Slack to receive real-time notifications about deal changes, "
        "new leads, and support tickets. Setup: 1) Install the NovaCRM Slack app from our "
        "integrations marketplace (Settings > Integrations > Slack). 2) Authorize the app to "
        "post to your chosen channel. 3) Configure notification rules: you can filter by event "
        "type (deal_won, deal_lost, new_lead, ticket_created), deal value threshold, customer "
        "tier, and assigned team member. 4) Optionally enable interactive buttons: when a new "
        "lead notification is posted, team members can click 'Claim' directly in Slack to "
        "assign the lead to themselves. Advanced: Use our Slack slash commands (/novacrm search "
        "[query], /novacrm deal [id]) to look up CRM data without leaving Slack. Enterprise "
        "customers can configure multiple channels with different notification rules — e.g., "
        "#sales-alerts for deal events and #support-escalations for high-priority tickets."
    ),
    (
        "Custom webhooks allow you to trigger external workflows when events occur in NovaCRM. "
        "Configuration: Go to Settings > Integrations > Webhooks > Add Endpoint. Provide your "
        "HTTPS endpoint URL (HTTP is not supported for security). Select the events you want "
        "to subscribe to: contact.created, contact.updated, deal.stage_changed, deal.won, "
        "deal.lost, ticket.created, ticket.resolved. Each webhook delivery includes a JSON "
        "payload with the event type, timestamp, and the full object state. Security: Every "
        "request includes an X-NovaCRM-Signature header containing an HMAC-SHA256 signature "
        "of the request body using your webhook secret. Always verify this signature before "
        "processing the event. Reliability: Failed deliveries are retried with exponential "
        "backoff (1s, 5s, 30s, 5m, 30m, 2h) up to 6 times over 3 hours. After all retries "
        "are exhausted, the webhook is marked as failed and you'll receive an email notification."
    ),
]


def seed_knowledge_articles(client: weaviate.Client) -> None:
    """Create and populate the KnowledgeArticle collection."""
    delete_collection_if_exists(client, "KnowledgeArticle")

    client.collections.create(
        name="KnowledgeArticle",
        properties=[
            weaviate.classes.config.Property(name="title", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="category", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="author", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="created_at", data_type=weaviate.classes.config.DataType.DATE),
        ],
    )
    print("  Created collection 'KnowledgeArticle'.")

    authors = [
        "Alice Chen", "Bob Martinez", "Carol Williams", "Emily Johnson",
        "Grace Liu", "Paul Schmidt", "Quinn Taylor", "Rachel Green",
        "George Bennett", "Helen Park",
    ]

    collection = client.collections.get("KnowledgeArticle")

    with collection.batch.dynamic() as batch:
        for i in range(200):
            created = fake.date_time_between(start_date="-2y", end_date="now")
            title = KB_TITLES[i % len(KB_TITLES)]
            content = KB_CONTENTS[i % len(KB_CONTENTS)]
            # Add slight variation
            suffix = (
                f" For additional help, contact {random.choice(authors)} or visit the "
                f"internal wiki page last updated on {fake.date_this_year().isoformat()}."
            )

            batch.add_object(properties={
                "title": title,
                "content": content + suffix,
                "category": random.choice(KB_CATEGORIES),
                "author": random.choice(authors),
                "created_at": created.isoformat() + "Z",
            })

    print(f"  Inserted 200 KnowledgeArticle objects.")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print("Weaviate seeder starting...")
    wait_for_weaviate()

    client = weaviate.connect_to_local()

    try:
        print("Seeding IncidentReport...")
        seed_incident_reports(client)

        print("Seeding KnowledgeArticle...")
        seed_knowledge_articles(client)

        print("Weaviate seeding complete.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
