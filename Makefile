.PHONY: up down seed seed-wait proto engine adapters ai studio all test

up:
	docker compose up -d

down:
	docker compose down

seed-wait:
	@echo "==> Waiting for services to be healthy..."
	@until docker compose exec postgres pg_isready -U atlas -d atlas >/dev/null 2>&1; do \
		echo "    Waiting for Postgres..."; sleep 3; done
	@until docker compose exec clickhouse curl -sf http://localhost:8123/ping >/dev/null 2>&1; do \
		echo "    Waiting for ClickHouse..."; sleep 3; done
	@until docker compose exec elasticsearch curl -sf http://localhost:9200/_cluster/health >/dev/null 2>&1; do \
		echo "    Waiting for Elasticsearch..."; sleep 3; done
	@until docker compose exec weaviate curl -sf http://localhost:8080/v1/.well-known/ready >/dev/null 2>&1; do \
		echo "    Waiting for Weaviate..."; sleep 3; done
	@echo "==> All services healthy."

seed: seed-wait
	@echo "==> Seeding Postgres (handled by docker-entrypoint-initdb.d mount)..."
	@echo "    Postgres init.sql runs automatically on first start."
	@echo "==> Seeding ClickHouse (handled by docker-entrypoint-initdb.d mount)..."
	@echo "    ClickHouse init.sql runs automatically on first start."
	@echo "==> Installing seed script dependencies..."
	pip install -q -r seed/requirements.txt
	@echo "==> Seeding Elasticsearch..."
	python seed/elasticsearch/seed.py
	@echo "==> Seeding Weaviate..."
	python seed/weaviate/seed.py
	@echo "==> All seed data loaded."

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
