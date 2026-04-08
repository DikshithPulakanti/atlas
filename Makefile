.PHONY: up down seed proto engine adapters ai studio all test

up:
	docker compose up -d

down:
	docker compose down

seed:
	@echo "==> Seeding Postgres..."
	docker compose exec postgres psql -U atlas -d atlas -f /seed/init.sql
	@echo "==> Seeding ClickHouse..."
	docker compose exec clickhouse clickhouse-client --query "$$(cat seed/clickhouse/init.sql)"
	@echo "==> Seeding Elasticsearch..."
	python seed/elasticsearch/seed.py
	@echo "==> Seeding Weaviate..."
	python seed/weaviate/seed.py
	@echo "==> Done."

proto:
	@echo "==> Generating protobuf code..."
	cd proto && buf generate
	@echo "==> Done."

engine:
	@echo "==> Building engine (Rust)..."
	cd engine && cargo build
	@echo "==> Done."

adapters:
	@echo "==> Building adapters (Go)..."
	cd adapters && go build ./cmd/server/
	@echo "==> Done."

ai:
	@echo "==> Installing ai-operators deps..."
	cd ai-operators && uv sync
	@echo "==> Done."

studio:
	@echo "==> Installing studio deps..."
	cd studio && pnpm install
	@echo "==> Done."

all: proto engine adapters ai studio
	@echo "==> All components built."

test:
	@echo "==> Running engine tests..."
	cd engine && cargo test
	@echo "==> Running adapters tests..."
	cd adapters && go test ./...
	@echo "==> Running ai-operators tests..."
	cd ai-operators && uv run pytest
	@echo "==> Running studio tests..."
	cd studio && pnpm test
	@echo "==> All tests passed."
