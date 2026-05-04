# app.py
# Flask Backend for Finance Dashboard with Authentication

from flask import Flask, jsonify, request, render_template, session, redirect
from flask_cors import CORS
import pymysql
import pandas as pd
import bcrypt
from dotenv import load_dotenv
import os
import analytics

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'finance123secret')

# ── DB Connection ──────────────────────────────────────────
def get_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

# ── Auth Helper ────────────────────────────────────────────
def logged_in():
    return 'user_id' in session

def current_user():
    return session.get('user_id')

# ── Page Routes ────────────────────────────────────────────
@app.route('/')
def index():
    if logged_in():
        return redirect('/welcome')
    return render_template('auth.html')

@app.route('/welcome')
def welcome():
    if not logged_in():
        return redirect('/')
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    if not logged_in():
        return redirect('/')
    return render_template('index.html')

# ── Register ───────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data     = request.json
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required!'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters!'}), 400

    db     = get_db()
    cursor = db.cursor()

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        db.close()
        return jsonify({'error': 'Email already registered!'}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed.decode('utf-8'))
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Account created successfully!'}), 201

# ── Login ──────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data     = request.json
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'All fields are required!'}), 400

    db     = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    db.close()

    if not user:
        return jsonify({'error': 'Email not found!'}), 401

    # Check password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Incorrect password!'}), 401

    # Set session
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    return jsonify({'message': 'Login successful!', 'name': user['name']}), 200

# ── Logout ─────────────────────────────────────────────────
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out!'}), 200

# ── Current User Info ──────────────────────────────────────
@app.route('/api/me')
def me():
    if not logged_in():
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({
        'id':   current_user(),
        'name': session.get('user_name')
    })

# ── Get All Expenses ───────────────────────────────────────
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.id, e.title, e.amount, e.expense_date, e.note, e.is_demo,
               c.name as category, c.icon, c.color
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s
        ORDER BY e.expense_date DESC
    """, (current_user(),))
    expenses = cursor.fetchall()
    for e in expenses:
        e['expense_date'] = str(e['expense_date'])
        e['amount']       = float(e['amount'])
    db.close()
    return jsonify(expenses)

# ── Add Expense ────────────────────────────────────────────
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    data   = request.json
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, amount, category_id, expense_date, note, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data['title'], data['amount'], data['category_id'],
          data['expense_date'], data.get('note', ''), current_user()))
    db.commit()
    db.close()
    return jsonify({'message': 'Expense added!'}), 201

# ── Edit Expense ───────────────────────────────────────────
@app.route('/api/expenses/<int:id>', methods=['PUT'])
def edit_expense(id):
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    data   = request.json
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE expenses
        SET title=%s, amount=%s, category_id=%s, expense_date=%s, note=%s
        WHERE id=%s AND user_id=%s
    """, (data['title'], data['amount'], data['category_id'],
          data['expense_date'], data.get('note', ''), id, current_user()))
    db.commit()
    db.close()
    return jsonify({'message': 'Expense updated!'})

# ── Delete Expense ─────────────────────────────────────────
@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id=%s AND user_id=%s",
        (id, current_user())
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Expense deleted!'})

# ── Get Categories ─────────────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def get_categories():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    db.close()
    return jsonify(categories)

# ── Analytics ──────────────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.id, e.title, e.amount, e.expense_date, e.note,
               c.name as category, c.icon, c.color
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s
    """, (current_user(),))
    expenses = cursor.fetchall()
    for e in expenses:
        e['expense_date'] = str(e['expense_date'])
        e['amount']       = float(e['amount'])
    db.close()
    return jsonify({
        'summary':    analytics.summary_stats(expenses),
        'categories': analytics.category_breakdown(expenses),
        'monthly':    analytics.monthly_trend(expenses),
        'insights':   analytics.ai_insights(expenses)
    })

# ── Load Demo Data ─────────────────────────────────────────
@app.route('/api/demo', methods=['POST'])
def load_demo():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    db     = get_db()
    cursor = db.cursor()

    # Clear existing demo data for this user
    cursor.execute(
        "DELETE FROM expenses WHERE is_demo=1 AND user_id=%s",
        (current_user(),)
    )

    # Load CSV with Pandas
    df = pd.read_csv('data/demo_data.csv')

    # Get category map
    cursor.execute("SELECT id, name FROM categories")
    cats = {c['name']: c['id'] for c in cursor.fetchall()}

    # Insert each row
    for _, row in df.iterrows():
        cat_id = cats.get(row['category'], cats['Other'])
        cursor.execute("""
            INSERT INTO expenses (title, amount, category_id, expense_date, note, is_demo, user_id)
            VALUES (%s, %s, %s, %s, %s, 1, %s)
        """, (row['title'], row['amount'], cat_id,
              row['date'], row.get('note', ''), current_user()))

    db.commit()
    db.close()
    return jsonify({'message': 'Demo data loaded!'})

# ── Clear Demo Data ────────────────────────────────────────
@app.route('/api/demo', methods=['DELETE'])
def clear_demo():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE is_demo=1 AND user_id=%s",
        (current_user(),)
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Demo data cleared!'})

# ── Run ────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)