from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db_connection


recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes')
def recipes_page():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT Recipes.r_id,
               Recipes.r_name,
               Users.username
        FROM Recipes
        JOIN Users
        ON Recipes.writer_id = Users.u_id
        ORDER BY Recipes.r_name
    ''')

    recipes = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('recipes.html', recipes=recipes)

@recipes_bp.route('/recipe/<int:r_id>')
def recipe_detail(r_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT r_name, description, instructions, cooking_time
        FROM Recipes
        WHERE r_id = %s
    ''', (r_id,))

    recipe = cur.fetchone()

    cur.execute('''
        SELECT Ingredients.ingredient_name,
               Recipe_Ingredients.quantity,
               Recipe_Ingredients.unit
        FROM Recipe_Ingredients
        JOIN Ingredients
        ON Recipe_Ingredients.i_id = Ingredients.i_id
        WHERE Recipe_Ingredients.r_id = %s
    ''', (r_id,))

    ingredients = cur.fetchall()

    cur.execute('''
        SELECT Users.username,
               Reviews.stars,
               Reviews.comment
        FROM Reviews
        JOIN Users
        ON Reviews.u_id = Users.u_id
        WHERE Reviews.r_id = %s
    ''', (r_id,))

    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'recipe_detail.html',
        recipe=recipe,
        ingredients=ingredients,
        reviews=reviews,
        r_id=r_id
    )


@recipes_bp.route('/add_review/<int:r_id>', methods=['POST'])
def add_review(r_id):
    stars = request.form['stars']
    comment = request.form['comment']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO Reviews (r_id, u_id, stars, comment)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (r_id, u_id)
        DO UPDATE SET
            stars = EXCLUDED.stars,
            comment = EXCLUDED.comment
    ''', (
        r_id,
        session['user_id'],
        stars,
        comment
    ))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('recipes.recipe_detail', r_id=r_id))