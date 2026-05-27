from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import get_db_connection

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

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO Users (username, email, u_password)
            VALUES (%s, %s, %s)
        ''', (username, email, password))

        conn.commit()

    except Exception as e:
        conn.rollback()
        flash('User already exists')
        print(e)

    cur.close()
    conn.close()

    return redirect(url_for('auth.login_page'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))