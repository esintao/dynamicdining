from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db_connection

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/stock')
def stock_page():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT Stock.s_id,
               Ingredients.ingredient_name,
               Stock.quantity,
               Stock.unit,
               Stock.expiry_date
        FROM Stock
        JOIN Ingredients
        ON Stock.i_id = Ingredients.i_id
        WHERE Stock.h_id = %s
    ''', (session['household_id'],))

    stock_items = cur.fetchall()

    cur.execute('SELECT i_id, ingredient_name FROM Ingredients ORDER BY ingredient_name')
    ingredients = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'stock.html',
        stock_items=stock_items,
        ingredients=ingredients
    )



@stock_bp.route('/add_stock', methods=['POST'])
def add_stock():
    i_id = request.form['i_id']
    quantity = request.form['quantity']
    unit = request.form['unit']
    expiry_date = request.form['expiry_date']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO Stock (h_id, i_id, quantity, unit, expiry_date)
        VALUES (%s, %s, %s, %s, %s)
    ''', (
        session['household_id'],
        i_id,
        quantity,
        unit,
        expiry_date
    ))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('stock.stock_page'))


@stock_bp.route('/delete_stock/<int:s_id>')
def delete_stock(s_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM Stock WHERE s_id = %s', (s_id,))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('stock.stock_page'))