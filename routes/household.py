from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import get_db_connection


household_bp = Blueprint('household', __name__)


@household_bp.route('/households')
def households():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT Household.h_id, Household.h_name
        FROM Household
        JOIN member_of
        ON Household.h_id = member_of.h_id
        WHERE member_of.u_id = %s
    ''', (session['user_id'],))

    households = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('households.html', households=households)


@household_bp.route('/select_household/<int:h_id>')
def select_household(h_id):
    session['household_id'] = h_id

    return redirect(url_for('household.home'))


@household_bp.route('/join_household')
def join_household_page():
    return render_template('join_household.html')

@household_bp.route('/join_household', methods=['POST'])
def join_household():
    h_name = request.form['h_name']
    h_password = request.form['h_password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT h_id
        FROM Household
        WHERE h_name = %s
        AND h_password = %s
    ''', (h_name, h_password))

    household = cur.fetchone()

    if household:
        h_id = household[0]

        cur.execute('''
            INSERT INTO member_of (u_id, h_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        ''', (session['user_id'], h_id))

        conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('household.households'))

@household_bp.route('/create_household', methods=['POST'])
def create_household():
    h_name = request.form['h_name']
    h_password = request.form['h_password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO Household (h_name, h_password)
        VALUES (%s, %s)
        RETURNING h_id
    ''', (h_name, h_password))

    h_id = cur.fetchone()[0]

    cur.execute('''
        INSERT INTO member_of (u_id, h_id)
        VALUES (%s, %s)
    ''', (session['user_id'], h_id))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('household.households'))

@household_bp.route('/home')
def home():
    if 'household_id' not in session:
        return redirect(url_for('household.households'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT Ingredients.ingredient_name,
               Stock.quantity,
               Stock.unit,
               Stock.expiry_date
        FROM Stock
        JOIN Ingredients
        ON Stock.i_id = Ingredients.i_id
        WHERE Stock.h_id = %s
        ORDER BY Stock.expiry_date ASC
    ''', (session['household_id'],))

    stock = cur.fetchall()

    cur.execute('''
        SELECT Recipes.r_id,
               Recipes.r_name,
               COUNT(*) AS matches
        FROM Recipes
        JOIN Recipe_Ingredients
        ON Recipes.r_id = Recipe_Ingredients.r_id
        JOIN Stock
        ON Recipe_Ingredients.i_id = Stock.i_id
        WHERE Stock.h_id = %s
        GROUP BY Recipes.r_id
        ORDER BY matches DESC
        LIMIT 5
    ''', (session['household_id'],))

    suggestions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'home.html',
        stock=stock,
        suggestions=suggestions
    )