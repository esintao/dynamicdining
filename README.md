# DynamicDining
App project for DIS 2026. Made by Esin Tao (cxq772) and Konrad Frederik Hänninen Pedersen (bjv627).

# Remarks
The E/R diagram can be found in the folder "ER_diagram" as "DynamicDining_ERdiagram.png." The purpose of this app it to allow users, that are connected to one or more households, to keep track of their pantries, fridges and freezers, and find new recipes based on what they have on stock. Users can write recipes, and review them. Users are only allowed to write one review per recipe to prevent spam. Users are also allowed to be a part of multiple households to accomodate divorced children, dorm students that want to keep track of their parents house etc. A certain ingredient can be apart of multiple instances in ones stock, to accomodate that you can have the same ingredient at home with multiple expiration dates.

The recipes come from food.com, from this link https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_interactions.csv. We have scraped the ingredients and their quantities and units using Regex. We also use Regex for user passwords in our application. 

Hope you enjoy :-)

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
docker-compose up --build
```
After running the application for the first time, you can just run the following:
```bash
docker-compose up
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

6. Change/create the file .env in the project
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
You can either use one of our premade accounts or create a new one.

## Login
You can login using the username "dualipa" and the password "password123". You can also use the other pre-made ones on users.csv.

>[!NOTE]
> These passwords do not follow the Regex rules we have stated for new users. We have given special privileges to ourselves and the famous singer, Dua Lipa.

You can also create a new user, using the link "Create account". Note new accounts must use a password with the given security rules. After creating a user, you get redirected into the login page.

## Choose household
In this page, you can choose a household (given that you are already in one) or create/join a household. You can create/join a household by pressing "Join or Create Household".

Users can be a part of multiple households, as we want our site to accomodate children of divorce, or students who frequently return from their dorm to their parents house :-)

When joining other households, you need a password. You can for example join the household thelipahouse, with the password password123.

When creating a household, you write a household name and a password that follows our security rules.

## Homepage
You will now enter the homepage, where you will see your current stock and recipe suggestions based on what you have in your stock.

## Stock manager
From the homepage on "Manage stock" or from the top bar through "Stock" you enter the stock manager. 

Here, you can see your current stock, update the items, and delete them. You can also add new items. Items are listed their ingredient name, quantity, unit and expiry date. You can add new items by selecting from a list of ingredients or add new ingredients to our database by writing them down.

## Recipe catalogue
From the top bar you can go to the recipe catalogue by pressing "Recipes".

Here, you can search for recipes based on their name and description, filter recipes by tags, filter recipes that only use your in-stock items and filter recipes by the ones you have written yourself or reviewed. 

### Recipe page
When pressing "View recipe" either through the recipe catalogue or the suggested recipes on the homepage, you will get a recipe, its description, ingredients and reviews.

You can also review a recipe here. Note - users can only review a recipe once. When trying to review a recipe again, the review will just be update. This is to prevent spam.

### Add recipe
From the recipe catalogue, users can add recipes by pressing "Add Your Recipe".

When creating a recipe, you must add a title. You should add the cooking time, a description, and tags that makes it easier for other users to find the recipe. When writing new tags not seen before in the database, these will be added to the database.

You should also add ingredients and the quantity and unit, the ingredients appear in, in the recipe e.g. "Flour - 200 - g".

You must add instructions to the recipe.

## Logout
When you're done, simply log out ("Logout").


