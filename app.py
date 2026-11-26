"""Flask frontend for the merged SQLite database."""

import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "merged_data.db"

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Order Dashboard</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --card: rgba(255, 255, 255, 0.88);
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #6366f1;
      --border: #e5e7eb;
      --shadow: 0 18px 45px rgba(31, 41, 55, 0.10);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 32px 20px 60px;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 12%, rgba(99, 102, 241, 0.15), transparent 42%),
        radial-gradient(circle at 88% 88%, rgba(14, 165, 233, 0.14), transparent 42%),
        var(--bg);
    }
    .wrap { max-width: 1120px; margin: 0 auto; }
    header {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 24px;
    }
    h1 {
      margin: 0;
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      letter-spacing: -0.03em;
    }
    .updated {
      color: var(--muted);
      font-size: 0.92rem;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(99, 102, 241, 0.12);
      color: var(--accent);
      font-size: 0.85rem;
      font-weight: 600;
    }
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
      animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.35; }
    }
    .card {
      margin-bottom: 24px;
      padding: 24px;
      background: var(--card);
      border: 1px solid rgba(255, 255, 255, 0.9);
      border-radius: 20px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }
    .card h2 {
      margin: 0 0 16px;
      font-size: 1.15rem;
    }
    .table-scroll { overflow-x: auto; }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.94rem;
    }
    th, td {
      padding: 11px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
    }
    th {
      color: var(--muted);
      font-weight: 600;
      background: rgba(243, 244, 246, 0.7);
    }
    tbody tr:last-child td { border-bottom: none; }
    tbody tr:hover { background: rgba(99, 102, 241, 0.05); }
    .num { text-align: right; }
    .summary { max-width: 520px; }
    .empty {
      padding: 18px;
      color: var(--muted);
      text-align: center;
    }
    @media (prefers-reduced-motion: reduce) {
      .dot { animation: none; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>Order Dashboard</h1>
        <div class="updated">Last updated: <span id="updated">{{ updated }}</span></div>
      </div>
      <span class="badge"><span class="dot"></span>Auto-refresh every 3 seconds</span>
    </header>

    <section class="card">
      <h2>Merged Orders</h2>
      <div class="table-scroll">
        <table id="orders">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer ID</th>
              <th>Customer</th>
              <th>Region</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Currency</th>
              <th class="num">Amount (CNY)</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section class="card summary">
      <h2>Average Amount (CNY) by Region</h2>
      <div class="table-scroll">
        <table id="summary">
          <thead>
            <tr>
              <th>Region</th>
              <th class="num">Average (CNY)</th>
              <th class="num">Orders</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
    const REFRESH_MS = 3000;

    function esc(value) {
      if (value === null || value === undefined) return '';
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    function renderOrders(rows) {
      const tbody = document.querySelector('#orders tbody');
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty">No merged orders found.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (r) {
        return '<tr>' +
          '<td>' + esc(r.order_id) + '</td>' +
          '<td>' + esc(r.customer_id) + '</td>' +
          '<td>' + esc(r.customer_name) + '</td>' +
          '<td>' + esc(r.region) + '</td>' +
          '<td>' + esc(r.order_date) + '</td>' +
          '<td>' + esc(r.amount) + '</td>' +
          '<td>' + esc(r.currency) + '</td>' +
          '<td class="num">' + esc(r.amount_cny) + '</td>' +
          '</tr>';
      }).join('');
    }

    function renderSummary(rows) {
      const tbody = document.querySelector('#summary tbody');
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty">No summary data found.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (r) {
        return '<tr>' +
          '<td>' + esc(r.region) + '</td>' +
          '<td class="num">' + esc(r.average_amount_cny) + '</td>' +
          '<td class="num">' + esc(r.order_count) + '</td>' +
          '</tr>';
      }).join('');
    }

    async function refresh() {
      try {
        const response = await fetch('/api/data', { cache: 'no-store' });
        const data = await response.json();
        renderOrders(data.orders);
        renderSummary(data.summary);
        document.getElementById('updated').textContent = new Date().toLocaleTimeString();
      } catch (error) {
        console.error('Failed to refresh data:', error);
      }
    }

    refresh();
    setInterval(refresh, REFRESH_MS);
  </script>
</body>
</html>
"""


def fetch_tables() -> tuple[list[dict], list[dict]]:
    """Read the merged orders and region summary tables from SQLite."""
    if not DB_PATH.exists():
        return [], []

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        orders = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM merged_orders ORDER BY order_id"
            )
        ]
        summary = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM region_summary ORDER BY region"
            )
        ]
    finally:
        connection.close()

    return orders, summary


@app.route("/")
def index() -> str:
    orders, summary = fetch_tables()
    return render_template_string(
        TEMPLATE,
        updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/api/data")
def api_data():
    orders, summary = fetch_tables()
    return jsonify({"orders": orders, "summary": summary})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
