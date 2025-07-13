import matplotlib
matplotlib.use('Agg')  # ✅ Use non-GUI backend for server rendering

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
import matplotlib.cm as cm 
import matplotlib.ticker as ticker
import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sales.db')

def generate_charts(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get sales data by date
    if start_date and end_date:
        cursor.execute("SELECT date, SUM(amount) FROM sales WHERE date BETWEEN ? AND ? GROUP BY date", (start_date, end_date))
    else:
        cursor.execute("SELECT date, SUM(amount) FROM sales GROUP BY date")

    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    # Extract and sort
    dates, totals = zip(*data)
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    sorted_data = sorted(zip(dates, totals))
    dates, totals = zip(*sorted_data)

    # Convert to NumPy for smooth plotting
    x = np.arange(len(dates))
    y = np.array(totals)

    # 🌈 Gradient Color
    gradient_color = mcolors.LinearSegmentedColormap.from_list("custom_gradient", ['#ff6a00', '#ff2fab', '#5f76f3'])

    fig, ax = plt.subplots(figsize=(9, 6))
  

    # Smooth line (optional cubic interpolation)
    from scipy.interpolate import make_interp_spline
    xnew = np.linspace(x.min(), x.max(), 300)
    spl = make_interp_spline(x, y, k=3)
    y_smooth = spl(xnew)

    # Line plot
    ax.plot(xnew, y_smooth, color="#ff2f2f", linewidth=2.5)

    # Gradient fill below
    ax.fill_between(xnew, y_smooth, color="#f7dfe0", alpha=0.1)

    # Style tweaks
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%b') for d in dates], color='white', fontsize=9)
    ax.set_yticklabels(ax.get_yticks(), color='white', fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('static/chart1.png', facecolor=fig.get_facecolor())
    plt.close()
# def generate_charts(start_date=None, end_date=None):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     if start_date and end_date:
#         cursor.execute("SELECT date, SUM(amount) FROM sales WHERE date BETWEEN ? AND ? GROUP BY date", (start_date, end_date))
#     else:
#         cursor.execute("SELECT date, SUM(amount) FROM sales GROUP BY date")

#     data = cursor.fetchall()
#     conn.close()

#     if not data:
#         return

#     dates, totals = zip(*data)

#     # 💡 Start custom style
#     plt.style.use('ggplot')  # Try: 'ggplot', 'fivethirtyeight', 'bmh'

#     fig, ax = plt.subplots(figsize=(8, 5))
#     ax.plot(dates, totals, color='#1f77b4', linewidth=2.5, marker='o', markersize=6)

#     ax.set_title('📈 Sales Over Time', fontsize=16, fontweight='bold', color='#333')
#     ax.set_xlabel('Date', fontsize=12)
#     ax.set_ylabel('Total Sales (₹)', fontsize=12)
#     plt.xticks(rotation=45)
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     plt.savefig('static/chart1.png')
#     plt.close()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sales.db')

def generate_pie_chart(start_date=None, end_date=None, year=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query sales by product_type for given year (or all)
    if year:
        cursor.execute("""
            SELECT product_type, COUNT(*) 
            FROM sales 
            WHERE strftime('%Y', date) = ? 
            GROUP BY product_type
        """, (year,))
    else:
        cursor.execute("""
            SELECT product_type, COUNT(*) 
            FROM sales 
            GROUP BY product_type
        """)

    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    labels, counts = zip(*data)
    total = sum(counts)

    # Custom Colors (inspired by your image)
    cmap=cm.get_cmap('tab20')
    colors =[cmap(i/len(labels))for i in range(len(labels))]

    # Set background to dark
    plt.style.use('dark_background')

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="#FFFFFFFF")
    wedges, texts, autotexts = ax.pie(
        counts, 
        labels=None,
        autopct=lambda pct: f"{pct:.1f}%", 
        startangle=140, 
        colors=colors,
        wedgeprops=dict(width=0.4),
        pctdistance=0.8,
        textprops={'color':'white', 'weight':'bold','fontsize':10}
    )

    # Center text: total
    ax.text(0, 0, f'{total}', ha='center', va='center', fontsize=16, color='black', fontweight='bold')

    # Create custom legend
    ax.legend(
        wedges,
        [f"{label} ({count / total:.0%})" for label, count in zip(labels, counts)],
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        labelcolor='black',
        labelspacing=1.8
    )

    plt.tight_layout()
    plt.savefig('static/piechart.png', facecolor=fig.get_facecolor())
    plt.close()


# ------------------ Dynamic Grouped Bar Chart ------------------
def generate_dynamic_bar_chart(csv_path):
    df = pd.read_csv(csv_path)

    if df.shape[1] < 2:
        return

    x_labels = df.iloc[:, 0]  # First column
    series_names = df.columns[1:]

    x = np.arange(len(x_labels))
    total_series = len(series_names)
    width = 0.8 / total_series

    fig, ax = plt.subplots(figsize=(9, 6), facecolor='white')

    # 🔥 Auto orange gradient shades
    orange_cmap = cm.get_cmap('Oranges', total_series + 2)  # More variation
    bar_colors = [orange_cmap(i) for i in range(2, total_series + 2)]

    for i, subject in enumerate(series_names):
        ax.bar(x + i * width - (width * total_series / 2) + width/2,
               df[subject],
               width=width,
               label=subject,
               color=bar_colors[i],
               edgecolor='none')

    # ✨ Styling
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=0, ha='center', fontsize=10)

    ax.set_ylim(0, df[series_names].values.max() * 1.3)

    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    # Hide spines
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')

    # Grid and labels
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}'))
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), frameon=True, ncol=len(series_names))

    plt.tight_layout()
    plt.savefig("static/bar_dynamic.png", facecolor=fig.get_facecolor())
    plt.close()