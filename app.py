from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'cms.db'

# Create database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close database connection at the end of the request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create tables if they don't exist
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
                            id INTEGER PRIMARY KEY,
                            title TEXT,
                            content TEXT
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT
                        )''')
        db.commit()

# Initialize the database
init_db()

@app.route('/')
def index():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    return render_template('index.html', articles=articles)

@app.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (id,))
    article = cursor.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE articles SET title = ?, content = ? WHERE id = ?", (title, content, id))
        db.commit()
        return redirect(url_for('article', id=id))
    return render_template('article.html', article=article)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (id,))
    article = cursor.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE articles SET title = ?, content = ? WHERE id = ?", (title, content, id))
        db.commit()
        return redirect(url_for('article', id=id))
    return render_template('edit.html', article=article)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor = get_db().cursor()
        cursor.execute("INSERT INTO articles (title, content) VALUES (?, ?)", (title, content))
        get_db().commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cursor = get_db().cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        get_db().commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
