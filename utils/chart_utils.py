# utils/chart_utils.py

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
    plt.figure(figsize=(8, 4))
    plt.plot(dates, totals, marker='o')
    plt.title('Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/chart1.png')
    plt.close()
