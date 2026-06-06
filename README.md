DynamicDining
App project for DIS 2026. Made by Esin Tao (cxq772) and Konrad Frederik Hänninen Pedersen (bjv627).

# Execution guide
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

### Resetting database
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
### Prerequisites
Make sure you have the following
1. Python (3.8 or newer)
2. PostgreSQL (12 or higher)
3. Git (for cloning the repository)

### Installation
1. Clone the repository
```bash
git clone https://github.com/esintao/DynamicDining.git
```

Get into the folder. 
```bash
cd DynamicDining
```
2. Set up python environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
````

3. Install python dependencies
```bash
pip install -r requirements.txt
```

4. Create database on PostgreSQL
Connect to PostgresSQL
```bash
psql -U postgres
```

Create the database in postgres terminal. If you have pgAdmin, you can also make the database there.
```bash
CREATE DATABASE recipe_app;
```

5. Initialize schema
```bash
psql -U postgres -d recipe_app -f schemas.sql
```

6. Change the file .env in the project
Change the DB_PASSWORD value to match your own local PostgreSQL system password:
```python
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recipe_app
DB_USER=postgres
DB_PASSWORD=your_actual_local_password_here
````

7. Load initial data into relations
```bash
python import_all_csv_data.py
````

8. Run the app
```bash
python app.py
```
The app should run on: http://localhost:5000

### Troubleshooting
#### PostgreSQL Connection Errors

Error: psycopg2.OperationalError: could not connect to server

Solutions: 
1. Verify PostgreSQL is running: 
```bash
psql -U postgres -c "SELECT version();"
```

2. Check database credentials in .env match your PostgreSQL configuration

3. Ensure database recipe_app exists: 
```bash
psql -U postgres -l | grep recipe_app
```

4. Verify PostgreSQL is listening on the correct port (default: 5432)

#### Port Already in Use

Error: Address already in use

The Flask app is trying to use port 5000, but it's already occupied.

Solution: Modify app.py line 21: 
```python<
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True) # Change 5000 to another port
```

#### ModuleNotFoundError: No module named 'flask'

Solution: Ensure your virtual environment is activated and dependencies are installed: 
```bash 
# Activate virtual environment source 
venv/bin/activate # macOS/Linux 
# or
 venv\Scripts\activate # Windows

# Reinstall dependencies
 pip install -r requirements.txt
```

#### Database Schema Not Found

Error: Tables don't exist when running the app

Solution: Ensure you've initialized the schema: 
```bash
psql -U postgres -d recipe_app -f schemas.sql
```


---
### Resetting the Database

To clear all data and reset to a clean state:

```bash 
# Drop the database 
dropdb -U postgres recipe_app

# Recreate the database 
createdb -U postgres recipe_app

# Reinitialize schema 
psql -U postgres -d recipe_app -f schemas.sql

# Reload initial data (optional) 
python import_all_csv_data.py 
```

---

# Interaction instructions
