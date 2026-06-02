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
    i_id = request.form.get('i_id')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')
    
    if not i_id or not quantity or not unit:
        return redirect(url_for('stock.stock_page'))

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
        expiry_date if expiry_date else None
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('stock.stock_page'))


# --- UPDATED: HANDLES QUANTITY, UNIT, & EXPIRY ALL IN ONE GO ---
@stock_bp.route('/update_stock/<int:s_id>', methods=['POST'])
def update_stock(s_id):
    new_quantity = request.form.get('quantity')
    new_unit = request.form.get('unit')
    new_expiry = request.form.get('expiry_date')
    
    if new_quantity and new_unit:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE Stock 
            SET quantity = %s, unit = %s, expiry_date = %s 
            WHERE s_id = %s AND h_id = %s
        ''', (
            new_quantity, 
            new_unit, 
            new_expiry if new_expiry else None, 
            s_id, 
            session['household_id']
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

@stock_bp.route('/add_ingredient_db', methods=['POST'])
def add_ingredient_db():
    new_name = request.form.get('new_ingredient_name')
    if new_name:
        new_name = new_name.strip().lower()
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert only if it doesn't already exist to avoid duplicate entries
        cur.execute('''
            INSERT INTO Ingredients (ingredient_name)
            VALUES (%s)
            ON CONFLICT (ingredient_name) DO NOTHING
        ''', (new_name,))
        
        conn.commit()
        cur.close()
        conn.close()
        
    return redirect(url_for('stock.stock_page'))