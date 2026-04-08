"""Seed Elasticsearch with NovaCRM document data.

Creates three indices:
  - confluence_docs: internal engineering/product documentation
  - bug_reports: tracked bugs and issues
  - news_articles: tech industry news for enrichment demos

Idempotent: deletes and recreates indices on each run.
"""

import sys
import time
import random
from datetime import datetime, timedelta

import requests
from elasticsearch import Elasticsearch, helpers
from faker import Faker

ES_URL = "http://localhost:9200"
fake = Faker()
Faker.seed(42)
random.seed(42)


def wait_for_es(timeout: int = 60) -> None:
    """Block until Elasticsearch is healthy."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{ES_URL}/_cluster/health", timeout=5)
            if r.ok and r.json().get("status") in ("green", "yellow"):
                print("Elasticsearch is healthy.")
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    print("ERROR: Elasticsearch not ready after timeout.", file=sys.stderr)
    sys.exit(1)


def recreate_index(es: Elasticsearch, name: str, mappings: dict) -> None:
    """Delete index if exists, then create with mappings."""
    if es.indices.exists(index=name):
        es.indices.delete(index=name)
        print(f"  Deleted existing index '{name}'.")
    es.indices.create(index=name, mappings=mappings.get("mappings", {}))
    print(f"  Created index '{name}'.")


# =============================================================================
# 1. confluence_docs — 300 internal documents
# =============================================================================

SPACES = ["Engineering", "Product", "Sales", "Support"]
DOC_TYPES = ["decision_record", "meeting_notes", "design_doc", "runbook", "postmortem"]
TAGS_POOL = [
    "architecture", "api", "database", "migration", "performance", "security",
    "monitoring", "kubernetes", "ci-cd", "frontend", "backend", "ml-pipeline",
    "billing", "onboarding", "compliance", "testing", "release", "incident",
    "scaling", "cost-optimization",
]
AUTHORS = [
    "Alice Chen", "Bob Martinez", "Carol Williams", "Emily Johnson",
    "Grace Liu", "Irene Dubois", "Jack Thompson", "George Bennett",
    "Helen Park", "Ivan Volkov",
]

CONFLUENCE_TITLES = [
    "ADR-{n}: Migrate from PostgreSQL 14 to 16",
    "ADR-{n}: Adopt gRPC for inter-service communication",
    "ADR-{n}: Switch from REST to GraphQL for public API",
    "ADR-{n}: Choose ClickHouse for analytics workload",
    "ADR-{n}: Implement CQRS pattern for contacts service",
    "Design: Real-time pipeline notification system",
    "Design: Multi-tenant data isolation strategy",
    "Design: API rate limiting v2 with sliding window",
    "Design: Customer health score ML model",
    "Design: Webhook delivery reliability improvements",
    "Design: Search infrastructure migration to Elasticsearch 8",
    "Design: Event sourcing for audit trail",
    "Runbook: Database failover procedure",
    "Runbook: Elasticsearch cluster recovery",
    "Runbook: Kubernetes node replacement",
    "Runbook: Redis cache invalidation emergency flush",
    "Runbook: API gateway circuit breaker tuning",
    "Runbook: ML pipeline GPU allocation scaling",
    "Postmortem: 2024-03-15 API outage (45 minutes)",
    "Postmortem: 2024-05-22 data sync failure affecting 12 customers",
    "Postmortem: 2024-07-01 billing calculation error",
    "Postmortem: 2024-08-10 search index corruption",
    "Postmortem: 2024-09-30 authentication service degradation",
    "Meeting: Q1 2024 architecture review",
    "Meeting: Frontend performance optimization sprint kickoff",
    "Meeting: Security audit findings review",
    "Meeting: API versioning strategy discussion",
    "Meeting: Data retention policy alignment",
    "RFC: Introduce feature flags for gradual rollouts",
    "RFC: Unified error handling across microservices",
]

CONFLUENCE_BODIES = [
    (
        "This document outlines our decision to migrate from PostgreSQL 14 to PostgreSQL 16. "
        "The primary motivation is to leverage the new logical replication improvements and "
        "parallel query enhancements that will benefit our reporting workload. Our benchmarks "
        "show a 30% improvement in complex analytical queries that join across the customers, "
        "deals, and activities tables. The migration will be performed using pg_upgrade with "
        "a blue-green deployment strategy to minimize downtime. We estimate a 15-minute "
        "maintenance window for the final switchover. Risk mitigation includes maintaining "
        "a hot standby on the old version for 48 hours post-migration. The rollback plan "
        "involves redirecting the connection pool back to the PG14 instance. All application "
        "code has been tested against PG16 in our staging environment for the past two weeks "
        "with no compatibility issues detected."
    ),
    (
        "After evaluating REST, gRPC, and Apache Thrift for our internal service communication, "
        "we've decided to adopt gRPC with Protocol Buffers. Key factors in this decision: "
        "1) Strong typing via proto definitions catches integration errors at compile time. "
        "2) Bidirectional streaming enables our real-time pipeline notification use case. "
        "3) Code generation for Go, Rust, and Python aligns with our polyglot stack. "
        "4) HTTP/2 multiplexing reduces connection overhead between services. We will maintain "
        "our REST/JSON public API for external consumers and use gRPC exclusively for internal "
        "service-to-service calls. The migration will be phased: adapter service first, then "
        "the query engine, and finally the AI operators. Proto schemas will live in a shared "
        "repository managed by Buf. Estimated completion: 6 weeks."
    ),
    (
        "Incident summary: On March 15, 2024, the NovaCRM API experienced a 45-minute outage "
        "starting at 14:23 UTC. The root cause was a deadlock in the connection pool manager "
        "triggered by a long-running migration query that was accidentally executed against "
        "production instead of staging. Impact: approximately 3,400 API requests failed with "
        "503 errors, affecting 89 active customers. Detection: PagerDuty alert fired at 14:25 "
        "when error rate exceeded 5% threshold. Resolution: the on-call engineer (Alice Chen) "
        "identified the rogue query via pg_stat_activity and terminated it at 15:08. Recovery "
        "was immediate once the connection pool drained. Action items: 1) Implement production "
        "query execution safeguards with statement_timeout=30s. 2) Add connection pool deadlock "
        "detection with automatic recovery. 3) Require peer review for all migration scripts. "
        "4) Add staging/production environment indicators to all admin tools."
    ),
    (
        "This design document proposes a multi-tenant data isolation strategy for NovaCRM. "
        "Currently we use a shared-schema approach where all customers' data lives in the same "
        "tables with a customer_id column. While this is operationally simple, enterprise customers "
        "are increasingly requesting data isolation guarantees for compliance reasons. Our proposed "
        "approach is a hybrid model: starter and professional tier customers continue using shared "
        "tables, while enterprise customers get their own PostgreSQL schema. The query engine will "
        "route queries based on the customer's isolation level, which is stored in the account "
        "metadata. This approach balances operational complexity with compliance requirements. "
        "The adapter layer will abstract the schema routing so that upstream services remain unaware "
        "of the isolation strategy. Performance testing shows less than 2ms overhead for schema "
        "switching per request."
    ),
    (
        "Sprint kickoff notes for the frontend performance optimization initiative. Current state: "
        "Lighthouse score is 62 on the main dashboard page. Target: 85+ by end of sprint. Key areas "
        "identified: 1) The contacts list renders all 10,000 rows on mount — need to implement "
        "virtualized scrolling. 2) The chart library (recharts) bundles 450KB uncompressed — evaluate "
        "switching to lightweight alternatives or lazy loading. 3) No image optimization pipeline — "
        "implement next/image for automatic WebP conversion and responsive sizing. 4) API calls on the "
        "dashboard fire sequentially — parallelize with React Suspense boundaries. 5) The global state "
        "store triggers unnecessary re-renders across unrelated components. Assignments: Carol owns the "
        "virtualization work, Daniel handles chart library evaluation, Maria takes image optimization."
    ),
    (
        "This runbook covers the procedure for Elasticsearch cluster recovery after a node failure. "
        "Prerequisites: kubectl access to the production cluster, ES admin credentials from Vault. "
        "Step 1: Verify cluster health via GET /_cluster/health. If status is red, identify unassigned "
        "shards with GET /_cat/shards?v&h=index,shard,prirep,state,unassigned.reason. Step 2: Check "
        "if the failed node is recoverable — inspect pod logs with kubectl logs es-data-N. If the node "
        "has a persistent disk failure, replace the PVC and let the shard recovery process redistribute "
        "data from replicas. Step 3: Monitor recovery progress with GET /_cat/recovery. Expected time: "
        "10-30 minutes depending on shard size. Step 4: Once cluster is green, verify search and "
        "indexing functionality with a smoke test query. Alert the team in #eng-incidents if recovery "
        "takes longer than 45 minutes."
    ),
    (
        "API rate limiting v2 design: We're replacing our current fixed-window rate limiter with a "
        "sliding window algorithm backed by Redis. The current implementation allows burst traffic at "
        "window boundaries, which caused the March 2024 overload incident. The new design uses a sorted "
        "set per customer per endpoint in Redis, where each entry's score is the request timestamp. "
        "Counting requests in the sliding window is an O(log N) ZRANGEBYSCORE operation. We'll keep the "
        "global limit at 1000 req/min per customer but add per-endpoint sub-limits: /contacts at 500, "
        "/deals at 300, /activities at 200, /reports at 100. Enterprise customers get 3x multipliers. "
        "Rate limit headers (X-RateLimit-Remaining, X-RateLimit-Reset) will be returned on every "
        "response. When a customer hits 80% of their limit, we'll emit a warning event to our "
        "monitoring pipeline."
    ),
    (
        "Security audit findings from the Q3 2024 penetration test conducted by CyberShield Inc. "
        "Critical findings (0): None. High findings (2): 1) JWT tokens do not expire for 24 hours — "
        "reduce to 1 hour with refresh token rotation. 2) The /admin/impersonate endpoint lacks "
        "audit logging — all impersonation events must be recorded with the admin user, target user, "
        "timestamp, and IP address. Medium findings (4): 1) CORS policy allows wildcard origins in "
        "staging — restrict to known domains. 2) Error responses include stack traces in non-production "
        "environments — ensure all environments return sanitized errors. 3) Database connection strings "
        "are passed via environment variables without encryption at rest. 4) The CSV export endpoint "
        "does not enforce row-level access control. Remediation deadline: High findings within 2 weeks, "
        "Medium within 30 days."
    ),
    (
        "Customer health score ML model design. The model predicts the likelihood of customer churn "
        "within the next 90 days on a 0-100 score. Features: daily_active_users trend (30-day slope), "
        "support ticket frequency and severity, API usage volume change, login frequency, feature "
        "adoption breadth (number of distinct features used), NPS survey score, billing payment "
        "timeliness, contract renewal date proximity. Architecture: a gradient boosted tree model "
        "trained on historical churn data from 2022-2023 (n=847 churned, n=4,203 retained). The model "
        "runs daily as a batch job in our ML pipeline, scoring all active customers. Results are "
        "written to the customer_health_scores table and surfaced in the account manager dashboard. "
        "Current AUC-ROC: 0.87. F1 at threshold 0.5: 0.72. We plan to A/B test proactive outreach "
        "triggered at score < 40."
    ),
    (
        "RFC: Unified error handling across microservices. Problem: Each service currently defines "
        "its own error format, making it difficult for the query engine to provide consistent error "
        "messages to end users. The adapter service returns Go-style errors, the AI operators return "
        "FastAPI HTTPExceptions, and the engine has custom Rust error types. Proposal: Define a "
        "standard error proto message in our shared schema with fields for error_code (enum), message "
        "(human-readable), details (structured metadata), and retry_after (for transient errors). "
        "All gRPC services will map their internal errors to this format at the service boundary. "
        "The query engine will aggregate errors from multiple sources and present a unified error "
        "response. Error codes will follow a hierarchical naming convention: SOURCE_UNAVAILABLE, "
        "QUERY_SYNTAX_ERROR, AI_OPERATOR_FAILED, PERMISSION_DENIED, RATE_LIMITED, etc."
    ),
]


def seed_confluence_docs(es: Elasticsearch) -> None:
    """Create and populate the confluence_docs index."""
    mappings = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "space": {"type": "keyword"},
                "type": {"type": "keyword"},
                "content": {"type": "text", "analyzer": "english"},
                "author": {"type": "keyword"},
                "created_at": {"type": "date"},
                "tags": {"type": "keyword"},
            }
        }
    }
    recreate_index(es, "confluence_docs", mappings)

    docs = []
    for i in range(300):
        title_template = CONFLUENCE_TITLES[i % len(CONFLUENCE_TITLES)]
        title = title_template.format(n=100 + i)
        body = CONFLUENCE_BODIES[i % len(CONFLUENCE_BODIES)]
        # Add variation to each doc
        suffix = (
            f" Last updated by {random.choice(AUTHORS)} on "
            f"{fake.date_between(start_date='-1y', end_date='today')}. "
            f"Related to project {fake.catch_phrase().lower()}."
        )
        docs.append({
            "_index": "confluence_docs",
            "_id": str(i + 1),
            "title": title,
            "space": random.choice(SPACES),
            "type": random.choice(DOC_TYPES),
            "content": body + suffix,
            "author": random.choice(AUTHORS),
            "created_at": fake.date_time_between(
                start_date="-2y", end_date="now"
            ).isoformat(),
            "tags": random.sample(TAGS_POOL, k=random.randint(2, 5)),
        })

    helpers.bulk(es, docs)
    print(f"  Indexed {len(docs)} confluence_docs.")


# =============================================================================
# 2. bug_reports — 400 tracked bugs
# =============================================================================

BUG_COMPONENTS = ["api", "web", "database", "auth", "billing"]
BUG_SEVERITIES = ["low", "medium", "high", "critical"]
BUG_STATUSES = ["open", "in_progress", "resolved", "wontfix"]

BUG_TITLES = [
    "Null pointer exception in contact merge operation",
    "Slow query on deals dashboard for large accounts",
    "CSRF token validation fails after session refresh",
    "Webhook retry logic ignores exponential backoff",
    "CSV export truncates unicode characters",
    "Search autocomplete returns stale results",
    "Billing proration calculation off by one day",
    "OAuth2 refresh token rotation race condition",
    "Memory leak in WebSocket connection handler",
    "Pagination breaks when filter changes mid-scroll",
    "Email template rendering fails with special characters",
    "API key rotation does not invalidate old keys immediately",
    "Dashboard chart tooltip shows wrong date format",
    "Concurrent deal updates cause lost writes",
    "Activity feed skips entries during high-volume periods",
    "Mobile viewport layout broken on iPad landscape",
    "GraphQL N+1 query on nested contacts resolver",
    "Timezone handling incorrect for AU/NZ customers",
    "File upload endpoint allows files larger than 50MB",
    "SSO logout does not clear all session cookies",
]

BUG_DESCRIPTIONS = [
    (
        "When a user attempts to merge two contacts that both have associated deals, "
        "the merge operation throws a NullPointerException at ContactMergeService.java:142. "
        "This happens because the deal association lookup returns null when the secondary "
        "contact has deals in a 'closed-lost' status. Affects approximately 5% of merge "
        "attempts. Workaround: manually reassign deals before merging."
    ),
    (
        "Customers with more than 50,000 deals experience 15+ second load times on the "
        "deals dashboard. The root cause is a missing index on the deals.stage_updated_at "
        "column combined with an N+1 query pattern in the stage history loader. The query "
        "plan shows a sequential scan on 2.3M rows. Adding a composite index on "
        "(customer_id, stage_updated_at) should reduce this to under 200ms."
    ),
    (
        "After a user's session is refreshed via the refresh token endpoint, the next CSRF "
        "token validation fails with a 403. This is because the CSRF token is bound to the "
        "old session ID, but the session refresh generates a new session ID without updating "
        "the CSRF token. Users must do a full page reload to recover. This is particularly "
        "annoying for users who leave tabs open overnight."
    ),
    (
        "The webhook delivery system is supposed to implement exponential backoff for failed "
        "deliveries (1s, 2s, 4s, 8s, ...) but the retry delay calculation has an integer "
        "overflow bug when the retry count exceeds 30, causing it to wrap to negative and "
        "retry immediately. This creates a thundering herd effect that overloads customer "
        "webhook endpoints. Seen in production for 3 customers so far."
    ),
    (
        "When exporting contacts to CSV, any field containing non-ASCII characters (e.g., "
        "Japanese company names, accented European names) gets truncated at the first "
        "multi-byte character. The issue is in the CSV writer which uses byte-length instead "
        "of character-length for field width calculations. Affects all customers with "
        "international data. Reported by 7 enterprise customers this month."
    ),
    (
        "The billing proration engine calculates mid-cycle plan changes with an off-by-one "
        "error in the day count. When a customer upgrades on the 15th of a 30-day month, "
        "they're charged for 16 days instead of 15. The bug is in BillingCalculator.prorate() "
        "which uses inclusive date ranges (end - start + 1) but the business logic expects "
        "exclusive end dates. Total customer impact estimated at $2,400/month in overcharges."
    ),
    (
        "The WebSocket connection handler for real-time updates has a memory leak. Each "
        "disconnected client leaves behind an event listener that is never cleaned up. "
        "After approximately 10,000 connect/disconnect cycles, the server's heap usage grows "
        "by 500MB. In production, this manifests as increasing memory usage over 48-72 hours "
        "until the container hits its memory limit and gets OOM-killed. The pod restarts "
        "cleanly but active WebSocket connections are dropped."
    ),
    (
        "When two users update the same deal simultaneously, the last write wins without any "
        "conflict detection. This has caused several enterprise customers to lose important "
        "deal notes and stage changes. The current implementation uses simple UPDATE statements "
        "without optimistic locking. We need to add a version column and implement compare-and- "
        "swap semantics. The UI should show a conflict resolution dialog when a version mismatch "
        "is detected."
    ),
]


def seed_bug_reports(es: Elasticsearch) -> None:
    """Create and populate the bug_reports index."""
    mappings = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "description": {"type": "text", "analyzer": "english"},
                "severity": {"type": "keyword"},
                "status": {"type": "keyword"},
                "component": {"type": "keyword"},
                "reported_by": {"type": "keyword"},
                "created_at": {"type": "date"},
                "resolved_at": {"type": "date"},
            }
        }
    }
    recreate_index(es, "bug_reports", mappings)

    docs = []
    for i in range(400):
        created = fake.date_time_between(start_date="-1y", end_date="now")
        status = random.choice(BUG_STATUSES)
        resolved = None
        if status in ("resolved", "wontfix"):
            resolved = (created + timedelta(hours=random.randint(1, 720))).isoformat()

        docs.append({
            "_index": "bug_reports",
            "_id": str(i + 1),
            "title": BUG_TITLES[i % len(BUG_TITLES)] + f" (#{1000 + i})",
            "description": BUG_DESCRIPTIONS[i % len(BUG_DESCRIPTIONS)],
            "severity": random.choice(BUG_SEVERITIES),
            "status": status,
            "component": random.choice(BUG_COMPONENTS),
            "reported_by": random.choice(AUTHORS),
            "created_at": created.isoformat(),
            "resolved_at": resolved,
        })

    helpers.bulk(es, docs)
    print(f"  Indexed {len(docs)} bug_reports.")


# =============================================================================
# 3. news_articles — 200 tech industry articles
# =============================================================================

NEWS_SOURCES = ["TechCrunch", "Reuters", "Bloomberg", "The Verge", "Ars Technica",
                "Wired", "VentureBeat", "ZDNet", "The Information", "Protocol"]
NEWS_CATEGORIES = ["funding", "product_launch", "acquisition", "earnings",
                   "regulation", "ai", "security", "infrastructure"]

NEWS_TITLES = [
    "{company} raises ${amount}M Series {round} to expand AI-powered CRM platform",
    "{company} acquires {target} for ${amount}M to bolster data analytics capabilities",
    "{company} reports {percent}% revenue growth in Q{q} {year} earnings",
    "{company} launches new enterprise API platform with real-time sync",
    "EU regulators fine {company} ${amount}M for data privacy violations",
    "{company} open-sources its internal ML pipeline framework",
    "Security researchers discover critical vulnerability in {company}'s auth system",
    "{company} migrates to cloud-native architecture, reports 40% cost reduction",
    "{company} partners with {partner} to integrate AI-driven insights",
    "New study shows {percent}% of enterprises now use AI in their CRM workflows",
]

NEWS_BODIES = [
    (
        "{company} announced today that it has raised ${amount} million in a Series {round} "
        "funding round led by Sequoia Capital, with participation from Andreessen Horowitz "
        "and existing investors. The company plans to use the funds to expand its AI-powered "
        "CRM platform, which uses machine learning to predict customer churn and recommend "
        "engagement strategies. CEO {ceo} said the company has seen 3x revenue growth year- "
        "over-year and now serves over 2,000 enterprise customers. The round values the "
        "company at ${valuation} billion, making it one of the most valuable B2B SaaS "
        "startups in the CRM space."
    ),
    (
        "In a move to strengthen its data analytics capabilities, {company} has agreed to "
        "acquire {target}, a startup specializing in real-time data pipeline orchestration, "
        "for approximately ${amount} million in a mix of cash and stock. The acquisition will "
        "bring {target}'s team of 45 engineers into {company}'s platform division. The deal "
        "is expected to close in Q{q} {year}, subject to regulatory approval. Analysts see "
        "this as a defensive move against competitors who have been rapidly adding analytics "
        "features to their CRM platforms."
    ),
    (
        "{company} reported strong results for Q{q} {year}, with revenue of ${amount} million, "
        "up {percent}% year-over-year. The company added 340 new enterprise customers during "
        "the quarter, bringing its total customer count to over 8,500. Net revenue retention "
        "rate came in at 125%, indicating healthy expansion within existing accounts. CFO "
        "{cfo} noted that the company's AI features drove a 15% increase in average contract "
        "value compared to the prior year. The company raised its full-year guidance, now "
        "expecting revenue of ${fy_amount} million."
    ),
    (
        "A team of security researchers at {company} Security Labs has discovered a critical "
        "vulnerability affecting several major CRM platforms, including a widely-used "
        "authentication bypass that could allow attackers to access any customer account "
        "without credentials. The vulnerability, tracked as CVE-{year}-{cve}, affects the "
        "SAML-based single sign-on implementation used by enterprises. Patches have been "
        "released by all affected vendors. Organizations are urged to update immediately "
        "and review their access logs for signs of exploitation."
    ),
]

COMPANIES = ["Salesforce", "HubSpot", "Zoho", "Pipedrive", "Monday.com",
             "Zendesk", "Freshworks", "Braze", "Klaviyo", "Amplitude"]
PEOPLE = ["Sarah Mitchell", "David Park", "Jennifer Wu", "Michael Torres",
          "Amanda Singh", "Robert Chen", "Lisa Thompson", "James Kim"]


def seed_news_articles(es: Elasticsearch) -> None:
    """Create and populate the news_articles index."""
    mappings = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "body": {"type": "text", "analyzer": "english"},
                "source": {"type": "keyword"},
                "entities": {"type": "keyword"},
                "published_at": {"type": "date"},
                "category": {"type": "keyword"},
            }
        }
    }
    recreate_index(es, "news_articles", mappings)

    docs = []
    for i in range(200):
        company = random.choice(COMPANIES)
        target = random.choice([c for c in COMPANIES if c != company])
        partner = random.choice([c for c in COMPANIES if c != company])
        amount = random.choice([25, 50, 75, 100, 150, 200, 350, 500])
        vals = {
            "company": company, "target": target, "partner": partner,
            "amount": amount, "round": random.choice(["B", "C", "D", "E"]),
            "percent": random.randint(15, 85), "q": random.randint(1, 4),
            "year": random.choice([2024, 2025]), "ceo": random.choice(PEOPLE),
            "cfo": random.choice(PEOPLE), "valuation": round(amount * 0.08, 1),
            "fy_amount": amount * 4, "cve": f"{random.randint(10000, 99999)}",
        }
        title = NEWS_TITLES[i % len(NEWS_TITLES)].format(**vals)
        body = NEWS_BODIES[i % len(NEWS_BODIES)].format(**vals)
        entities = [company]
        if target in body:
            entities.append(target)
        entities.extend(random.sample(PEOPLE, k=random.randint(1, 2)))

        docs.append({
            "_index": "news_articles",
            "_id": str(i + 1),
            "title": title,
            "body": body,
            "source": random.choice(NEWS_SOURCES),
            "entities": entities,
            "published_at": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).isoformat(),
            "category": random.choice(NEWS_CATEGORIES),
        })

    helpers.bulk(es, docs)
    print(f"  Indexed {len(docs)} news_articles.")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print("Elasticsearch seeder starting...")
    wait_for_es()
    es = Elasticsearch(ES_URL)

    print("Seeding confluence_docs...")
    seed_confluence_docs(es)

    print("Seeding bug_reports...")
    seed_bug_reports(es)

    print("Seeding news_articles...")
    seed_news_articles(es)

    print("Elasticsearch seeding complete.")


if __name__ == "__main__":
    main()
