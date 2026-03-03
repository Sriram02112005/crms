from flask import Flask, render_template, request, redirect, session, url_for
import pymysql

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="campus_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# Home route
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                       (name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['role_id'] = user['role_id']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
