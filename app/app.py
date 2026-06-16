import os
import re
import operator
from flask import Flask, request, jsonify, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]

OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}

EQUATION_PATTERN = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*$"
)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Math Calculator</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 40px 16px; }
    .container { width: 100%; max-width: 560px; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 24px; color: #1a1a2e; }
    .card { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 24px; }
    form { display: flex; gap: 10px; }
    input[type=text] { flex: 1; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color .15s; }
    input[type=text]:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,.15); }
    button { padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: background .15s; }
    button:hover { background: #4f46e5; }
    .error { color: #dc2626; font-size: .875rem; margin-top: 10px; min-height: 1.2em; }
    h2 { font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; font-size: .75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .05em; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
    td { padding: 10px 0; border-bottom: 1px solid #f3f4f6; font-size: .9375rem; color: #111827; }
    td:last-child { text-align: right; font-weight: 600; color: #6366f1; }
    .empty { color: #9ca3af; font-size: .9rem; text-align: center; padding: 20px 0; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Math Calculator</h1>
    <div class="card">
      <form id="calcForm">
        <input type="text" id="equation" placeholder="e.g. 12 * 3.5" autocomplete="off">
        <button type="submit">Calculate</button>
      </form>
      <div class="error" id="error"></div>
    </div>
    <div class="card">
      <h2>History</h2>
      <div id="history">
        <table>
          <thead><tr><th>Equation</th><th>Result</th></tr></thead>
          <tbody id="historyBody">
            <tr><td colspan="2" class="empty">No calculations yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <script>
    async function loadHistory() {
      const res = await fetch('/history');
      const data = await res.json();
      const tbody = document.getElementById('historyBody');
      if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" class="empty">No calculations yet.</td></tr>';
        return;
      }
      tbody.innerHTML = data.map(row =>
        `<tr><td>${row.equation}</td><td>${row.result}</td></tr>`
      ).join('');
    }

    document.getElementById('calcForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const eq = document.getElementById('equation').value.trim();
      const errEl = document.getElementById('error');
      errEl.textContent = '';
      const res = await fetch('/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({equation: eq}),
      });
      const data = await res.json();
      if (data.error) {
        errEl.textContent = data.error;
      } else {
        document.getElementById('equation').value = '';
        loadHistory();
      }
    });

    loadHistory();
  </script>
</body>
</html>"""


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    id SERIAL PRIMARY KEY,
                    equation TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True) or {}
    equation = (data.get("equation") or "").strip()

    m = EQUATION_PATTERN.match(equation)
    if not m:
        return jsonify({"error": "Enter a simple equation like: 5 + 3, 10 / 2, 4 * 7"}), 400

    a, op, b = float(m.group(1)), m.group(2), float(m.group(3))

    if op == "/" and b == 0:
        return jsonify({"error": "Division by zero is not allowed."}), 400

    result = OPERATORS[op](a, b)
    result_str = str(int(result)) if result == int(result) else str(round(result, 10)).rstrip("0")

    display = f"{m.group(1)} {op} {m.group(3)}"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO calculations (equation, result) VALUES (%s, %s)",
                (display, result_str),
            )

    return jsonify({"equation": display, "result": result_str})


@app.route("/history")
def history():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT equation, result FROM calculations ORDER BY id DESC")
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
