from flask import Flask, render_template, request, redirect, session, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="yourpassword",  # change this
        database="campus_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# Home
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                       (name, email, password))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# STEP 6 - View Resources
@app.route('/resources')
def resources():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resource")
    resources = cursor.fetchall()
    conn.close()

    return render_template('resources.html', resources=resources)

# STEP 7 - Book Resource
@app.route('/book/<int:resource_id>', methods=['POST'])
def book_resource(resource_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    booking_date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Prevent double booking
    cursor.execute("""
        SELECT * FROM booking
        WHERE resource_id=%s AND booking_date=%s
        AND status='Approved'
        AND (start_time < %s AND end_time > %s)
    """, (resource_id, booking_date, end_time, start_time))

    conflict = cursor.fetchone()

    if conflict:
        conn.close()
        return "Time slot already booked!"

    cursor.execute("""
        INSERT INTO booking (user_id, resource_id, booking_date, start_time, end_time)
        VALUES (%s,%s,%s,%s,%s)
    """, (user_id, resource_id, booking_date, start_time, end_time))

    conn.commit()
    conn.close()

    return redirect('/my-bookings')

# View My Bookings
@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, r.resource_name
        FROM booking b
        JOIN resource r ON b.resource_id = r.resource_id
        WHERE b.user_id=%s
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    conn.close()

    return render_template('my_bookings.html', bookings=bookings)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
