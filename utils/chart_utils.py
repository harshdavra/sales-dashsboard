import matplotlib
matplotlib.use('Agg')  # ✅ Use non-GUI backend for server rendering

import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sales.db')

def generate_charts(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Filter sales by date if provided
    if start_date and end_date:
        cursor.execute("SELECT date, SUM(amount) FROM sales WHERE date BETWEEN ? AND ? GROUP BY date", (start_date, end_date))
    else:
        cursor.execute("SELECT date, SUM(amount) FROM sales GROUP BY date")

    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    # Unzip dates and values
    dates, totals = zip(*data)

    # Chart 1: Sales over time
    plt.figure(figsize=(8, 7))
    plt.plot(dates, totals, marker='o')
    plt.title('Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/chart1.png')
    plt.close()

def generate_pie_chart(start_date=None, end_date=None, year=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ 1. If year is provided, use it
    if year:
        cursor.execute("""
            SELECT product_type, COUNT(*) 
            FROM sales 
            WHERE strftime('%Y', date) = ? 
            GROUP BY product_type
        """, (year,))
        title = f"Sales Distribution by Product Type ({year})"

    # ✅ 2. If start_date and end_date are provided
    elif start_date and end_date:
        cursor.execute("""
            SELECT product_type, COUNT(*) 
            FROM sales 
            WHERE date BETWEEN ? AND ? 
            GROUP BY product_type
        """, (start_date, end_date))
        title = f"Sales Distribution ({start_date} to {end_date})"

    # ✅ 3. Otherwise, show all data
    else:
        cursor.execute("""
            SELECT product_type, COUNT(*) 
            FROM sales 
            GROUP BY product_type
        """)
        title = "Sales Distribution by Product Type (All Time)"

    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    labels, counts = zip(*data)

    plt.figure(figsize=(5, 5))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=100)
    plt.title(title)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('static/piechart.png')
    plt.close()
