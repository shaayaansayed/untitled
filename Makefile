.PHONY: dev clean

dev:
	@echo "Setting up development environment..."
	@if [ -f .env ]; then \
		cp .env worker/; \
		cp .env backend/; \
		echo "✓ .env copied to worker/ and backend/"; \
	else \
		echo "⚠ Warning: .env file not found in root directory"; \
	fi
	docker compose -f docker-compose.dev.yml up --build

clean:
	@echo "Cleaning up copied .env files..."
	@rm -f worker/.env backend/.env
	@echo "✓ Cleaned up .env files"
