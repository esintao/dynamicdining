from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import get_db_connection
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login_page():
    return render_template('login.html')


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT u_id, username
        FROM Users
        WHERE username = %s
        AND u_password = %s
    ''', (username, password))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]

        return redirect(url_for('household.households'))

    flash('Invalid username or password')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/register')
def register_page():
    return render_template('register.html')

@auth_bp.route('/register_user', methods=['POST'])
def register_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if not validate_password_strength(password):
        flash('Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character.')
        return render_template('register.html', username=username, email=email)
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO Users (username, email, u_password)
            VALUES (%s, %s, %s)
        ''', (username, email, password))

        conn.commit()
        
        flash('Account successfully created! Please log in below.')
        
        cur.close()
        conn.close()
        return redirect(url_for('auth.login_page'))

    except Exception as e:
        conn.rollback()
        flash('User or email already exists. Please pick another.')
        print(e)
        
        cur.close()
        conn.close()
        #Stop and send them back to registration page on error
        return render_template('register.html', username=username, email=email)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))

def validate_password_strength(password):
    """
    Returns True if the password meets all security criteria:
    - At least 8 characters long
    - At least one uppercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&]", password):
        return False
    return True