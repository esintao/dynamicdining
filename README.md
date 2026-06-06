DynamicDining
App project for DIS 2026. Made by Esin Tao (cxq772) and Konrad Frederik Hänninen Pedersen (bjv627).

# Installation guide
## Running with docker

1. Clone the repository: 
```bash
git clone https://github.com/esintao/DynamicDining.git
```

Get into the folder. 
```bash
cd DynamicDining
```

2. Start the application: 
```bash
docker compose up --build
```
After running the application for the first time, you can just run the following:
```bash
docker compose up
```

Afterwards go into web server on http://localhost:5000 - PostgreSQL database on localhost:5432

The database schema will be automatically initialized from schemas.sql.

### Resetting data base
PostgreSQL data is persisted in a Docker volume. To reset the database: 
```bash
docker-compose down -v 
```

Then you can start the database again from
```bash
docker-compose up -v
```

### Troubleshooting
Port already in use: If port 5000 or 5432 is already in use, you can modify docker-compose.yml to use different ports. If you use MacOS, you will need to change the port in docker-compose.yml from 5000:5000 to something else (e.g. 5001:5000).

Database connection errors: Wait for the database to be ready. The web service has a dependency check that waits for PostgreSQL to be healthy before starting.

## Running without docker
