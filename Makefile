.PHONY: up up-prod down dev seed test logs build clean

# Start the development environment (hot-reloading enabled)
dev:
	docker compose -f docker-compose.dev.yml up --build

# Start the production environment
up-prod:
	docker compose up --build -d

# Stop all services
down:
	docker compose down
	docker compose -f docker-compose.dev.yml down

# Seed the database with demo data (must be run while environment is up)
seed:
	docker compose exec backend python -m scripts.seed_demo_data

# Run the test suite inside the docker container
test:
	docker compose exec backend python -m pytest tests/ -v

# View logs for all services
logs:
	docker compose logs -f

# Clean up dangling volumes and networks
clean:
	docker compose down -v
	docker compose -f docker-compose.dev.yml down -v
