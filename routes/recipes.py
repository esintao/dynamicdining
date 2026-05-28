from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db_connection


recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes')
def recipes_page():
    # 1. Grab filter/sort parameters from URL arguments
    search_query = request.args.get('search', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    stock_only = request.args.get('stock_only') == 'true'
    sort_by = request.args.get('sort_by', 'name') # Default sort

    # Fetch current household ID from session
    h_id = session.get('household_id') 

    conn = get_db_connection()
    cur = conn.cursor()

    # 2. Base Query with an added subquery to count matching stock ingredients
    query = f'''
        SELECT 
            r.r_id,
            r.r_name,
            u.username,
            r.cooking_time,
            r.description,
            COALESCE(AVG(rev.stars), 0) AS avg_stars,
            COUNT(DISTINCT rev.u_id) AS num_reviews,
            (
                SELECT COUNT(*)
                FROM Recipe_Ingredients ri
                JOIN Stock s ON ri.i_id = s.i_id
                WHERE ri.r_id = r.r_id AND s.h_id = %s AND s.quantity > 0
            ) AS matched_ingredients_count
        FROM Recipes r
        JOIN Users u ON r.writer_id = u.u_id
        LEFT JOIN Reviews rev ON r.r_id = rev.r_id
    '''
    
    # Track WHERE clauses and parameters safely (Starting with h_id for the subquery)
    where_clauses = []
    params = [h_id if h_id else 0] # Safe fallback if h_id isn't in session yet

    # Filter: Text search
    if search_query:
        where_clauses.append("(r.r_name ILIKE %s OR r.description ILIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Filter: Tag filter
    if tag_filter:
        where_clauses.append('''
            r.r_id IN (
                SELECT rt.r_id 
                FROM Recipe_Tags rt 
                JOIN Tags t ON rt.t_id = t.t_id 
                WHERE t.tag_name = %s
            )
        ''')
        params.append(tag_filter)

    # Filter: In-Stock Ingredients only
    if stock_only and h_id:
        where_clauses.append('''
            NOT EXISTS (
                SELECT 1 
                FROM Recipe_Ingredients ri
                WHERE ri.r_id = r.r_id
                AND ri.i_id NOT IN (
                    SELECT s.i_id 
                    FROM Stock s 
                    WHERE s.h_id = %s AND s.quantity > 0
                )
            )
        ''')
        params.append(h_id)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Group by required primary/joined columns
    query += " GROUP BY r.r_id, u.username"

    # 3. Dynamic Sorting (Including our new stock match sorting option!)
    if sort_by == 'stock_match' and h_id:
        query += " ORDER BY matched_ingredients_count DESC, r.r_name ASC"
    elif sort_by == 'cooking_time':
        query += " ORDER BY r.cooking_time ASC NULLS LAST"
    elif sort_by == 'num_reviews':
        query += " ORDER BY num_reviews DESC, r.r_name ASC"
    elif sort_by == 'avg_stars':
        query += " ORDER BY avg_stars DESC, r.r_name ASC"
    else:
        query += " ORDER BY r.r_name ASC" 

    cur.execute(query, tuple(params))
    recipes = cur.fetchall()

    # 4. Fetch all existing tags for the filter dropdown
    cur.execute("SELECT tag_name FROM Tags ORDER BY tag_name ASC")
    all_tags = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        'recipes.html', 
        recipes=recipes, 
        all_tags=all_tags,
        search_query=search_query,
        selected_tag=tag_filter,
        stock_only=stock_only,
        sort_by=sort_by
    )

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