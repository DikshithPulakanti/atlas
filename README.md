# Atlas

A unified query engine for heterogeneous data sources with AI-powered operators.

## Architecture

- **engine/** — Rust: AtlasQL compiler + execution engine
- **adapters/** — Go: Source adapter layer (Postgres, ClickHouse, Elasticsearch, Weaviate, Parquet)
- **ai-operators/** — Python: AI operator service (sentiment, summarize, classify, similarity, explain, embed)
- **studio/** — TypeScript: Next.js 15 frontend (query editor, schema explorer, history, dashboard)
- **proto/** — Shared Protobuf schemas (buf-managed)

## Quick Start

```bash
make up        # Start all infrastructure services
make seed      # Load seed data
make all       # Build everything
make test      # Run all test suites
```

## Prerequisites

- Rust 1.78+
- Go 1.22+
- Python 3.12+ / uv
- Node.js 20+ / pnpm
- Docker & Docker Compose
- buf (protobuf toolchain)
