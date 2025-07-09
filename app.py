from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from utils.chart_utils import generate_charts
import os

app = Flask(__name__)
app.secret_key = "123456789harsh"

# Path to your SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'sales.db')


# ------------------------- DATABASE HELPERS -------------------------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------- ROUTES ---------------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?',
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    generate_charts()  # Generate chart1.png, chart2.png
    return render_template('dashboard.html')


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product = request.form['product']
        amount = request.form['amount']
        date = request.form['date']
        added_by = session['user']

        conn = get_db_connection()
        conn.execute('INSERT INTO sales (product, amount, date, added_by) VALUES (?, ?, ?, ?)',
                     (product, amount, date, added_by))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add-sale.html')


@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales ORDER BY date DESC').fetchall()
    conn.close()

    return render_template('history.html', sales=sales)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect(url_for('login'))

    sales = []
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        conn = get_db_connection()
        sales = conn.execute('SELECT * FROM sales WHERE date BETWEEN ? AND ?',
                             (start_date, end_date)).fetchall()
        conn.close()

        generate_charts(start_date, end_date)

    return render_template('report.html', sales=sales)


@app.route('/upload-csv', methods=['GET', 'POST'])
def upload_csv():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)

            import csv
            conn = get_db_connection()
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    conn.execute('INSERT INTO sales (product, amount, date, added_by) VALUES (?, ?, ?, ?)',
                                 (row[0], row[1], row[2], session['user']))
            conn.commit()
            conn.close()

            return redirect(url_for('history'))

    return render_template('upload-csv.html')
# ----------------- UPDATE SALE -----------------
@app.route('/update_sale/<int:sale_id>', methods=['GET', 'POST'])
def update_sale(sale_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        product = request.form['product']
        amount = request.form['amount']
        date = request.form['date']

        conn.execute('UPDATE sales SET product=?, amount=?, date=? WHERE id=?',
                     (product, amount, date, sale_id))
        conn.commit()
        conn.close()
        return redirect(url_for('history'))

    sale = conn.execute('SELECT * FROM sales WHERE id=?', (sale_id,)).fetchone()
    conn.close()

    if not sale:
        return "Sale not found", 404

    return render_template('update-sale.html', sale=sale)


# ----------------- DELETE SALE -----------------
@app.route('/delete-sale/<int:sale_id>')
def delete_sale(sale_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM sales WHERE id=?', (sale_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('history'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# --------------------------- MAIN ---------------------------

if __name__ == '__main__':
    app.run(debug=True)
