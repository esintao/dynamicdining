from flask import Flask
from routes.auth import auth_bp
from routes.household import household_bp
from routes.stock import stock_bp
from routes.recipes import recipes_bp



app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.register_blueprint(auth_bp)
app.register_blueprint(household_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(recipes_bp)

print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)