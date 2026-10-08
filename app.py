import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_chef_hanaa_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    categories = db.session.query(Recipe.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    selected_category = request.args.get('category')
    if selected_category:
        recipes = Recipe.query.filter_by(category=selected_category).all()
    else:
        recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes, categories=categories, selected_category=selected_category)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    recipes = Recipe.query.all()
    return render_template('admin_dashboard.html', recipes=recipes)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_recipe():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        image_url = request.form.get('image_url')
        new_recipe = Recipe(title=title, category=category, ingredients=ingredients, instructions=instructions, image_url=image_url)
        db.session.add(new_recipe)
        db.session.commit()
        flash('تمت إضافة الوصفة بنجاح!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_recipe.html')

@app.route('/admin/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    flash('تم حذف الوصفة بنجاح.', 'warning')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run()
