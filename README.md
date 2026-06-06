DynamicDining
App project for DIS 2026. Made by Esin Tao (cxq772) and Konrad Frederik Hänninen Pedersen (bjv627).

## Running with Docker

### Prerequisites - Docker - Docker Compose

### Quick Start

1. Clone the repository: bash<span data-diff-end="10"></span> <span data-diff-start="11"></span>git clone <repository-url><span data-diff-end="11"></span> <span data-diff-start="12"></span>cd DynamicDining<span data-diff-end="12"></span> <span data-diff-start="13"></span>

2. Start the application: bash<span data-diff-end="16"></span> <span data-diff-start="17"></span>docker-compose up<span data-diff-end="17"></span> <span data-diff-start="18"></span>

This will start: - Flask web server on http://localhost:5000 - PostgreSQL database on localhost:5432

The database schema will be automatically initialized from schemas.sql.

### Common Commands

Start the application: bash<span data-diff-end="29"></span> <span data-diff-start="30"></span>docker-compose up<span data-diff-end="30"></span> <span data-diff-start="31"></span>

Start in background: bash<span data-diff-end="34"></span> <span data-diff-start="35"></span>docker-compose up -d<span data-diff-end="35"></span> <span data-diff-start="36"></span>

Stop the application: bash<span data-diff-end="39"></span> <span data-diff-start="40"></span>docker-compose down<span data-diff-end="40"></span> <span data-diff-start="41"></span>

View logs: bash<span data-diff-end="44"></span> <span data-diff-start="45"></span>docker-compose logs -f web<span data-diff-end="45"></span> <span data-diff-start="46"></span>

Rebuild the Docker image (after code changes): bash<span data-diff-end="49"></span> <span data-diff-start="50"></span>docker-compose build --no-cache<span data-diff-end="50"></span> <span data-diff-start="51"></span>

### Environment Variables

Database connection is configured in docker-compose.yml. Default values: - DB_HOST: postgres - DB_USER: postgres - DB_PASSWORD: 6452 - DB_NAME: recipe_app - DB_PORT: 5432

### Database

PostgreSQL data is persisted in a Docker volume. To reset the database: bash<span data-diff-end="65"></span> <span data-diff-start="66"></span>docker-compose down -v # -v removes volumes<span data-diff-end="66"></span> <span data-diff-start="67"></span>docker-compose up # reinitialize<span data-diff-end="67"></span> <span data-diff-start="68"></span>

### Troubleshooting

Port already in use: If port 5000 or 5432 is already in use, you can modify docker-compose.yml to use different ports.

Database connection errors: Wait for the database to be ready. The web service has a dependency check that waits for PostgreSQL to be healthy before starting.