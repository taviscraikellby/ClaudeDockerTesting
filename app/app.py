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
    :root {
      --bg: #0f0f1a;
      --surface: #1a1a2e;
      --surface2: #16213e;
      --border: #2a2a4a;
      --text: #e8e8f0;
      --text-muted: #8888aa;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --error: #f87171;
      --result: #a5b4fc;
    }
    body.light {
      --bg: #f0f2f5;
      --surface: #ffffff;
      --surface2: #f8f9fb;
      --border: #e5e7eb;
      --text: #111827;
      --text-muted: #6b7280;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --error: #dc2626;
      --result: #4f46e5;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); display: flex; justify-content: center; padding: 40px 16px; transition: background .2s, color .2s; }
    .container { width: 100%; max-width: 560px; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    h1 { font-size: 1.5rem; font-weight: 600; color: var(--text); }
    .theme-toggle { background: var(--surface); border: 1px solid var(--border); color: var(--text-muted); padding: 6px 14px; border-radius: 20px; font-size: .8125rem; cursor: pointer; transition: all .15s; }
    .theme-toggle:hover { border-color: var(--accent); color: var(--accent); }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 24px; }
    .error { color: var(--error); font-size: .875rem; margin-top: 12px; min-height: 1.2em; text-align: center; }
    h2 { font-size: .75rem; font-weight: 600; color: var(--text-muted); margin-bottom: 16px; text-transform: uppercase; letter-spacing: .05em; }

    /* Display */
    .display { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; min-height: 72px; display: flex; flex-direction: column; align-items: flex-end; justify-content: flex-end; gap: 4px; }
    .display-expr { font-size: .9rem; color: var(--text-muted); min-height: 1.2em; word-break: break-all; }
    .display-val { font-size: 2rem; font-weight: 300; color: var(--text); word-break: break-all; }

    /* Presets */
    .presets { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .preset-btn { background: var(--surface2); border: 1px solid var(--border); color: var(--text-muted); padding: 6px 12px; border-radius: 20px; font-size: .8125rem; cursor: pointer; transition: all .15s; }
    .preset-btn:hover { border-color: var(--accent); color: var(--accent); }

    /* Keypad */
    .keypad { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    .key { padding: 0; height: 60px; border: 1px solid var(--border); border-radius: 10px; font-size: 1.125rem; cursor: pointer; transition: background .1s, transform .08s; display: flex; align-items: center; justify-content: center; user-select: none; }
    .key:active { transform: scale(.94); }
    .key-digit { background: var(--surface2); color: var(--text); }
    .key-digit:hover { background: var(--border); }
    .key-op { background: var(--surface); color: var(--accent); border-color: var(--accent); font-size: 1.25rem; }
    .key-op:hover { background: var(--accent); color: white; }
    .key-clear { background: var(--surface); color: var(--error); border-color: var(--error); }
    .key-clear:hover { background: var(--error); color: white; }
    .key-eq { background: var(--accent); color: white; border-color: var(--accent); font-size: 1.25rem; }
    .key-eq:hover { background: var(--accent-hover); }
    .key-zero { grid-column: span 2; }

    /* History */
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; font-size: .75rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .05em; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
    td { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: .9375rem; color: var(--text); }
    td:last-child { text-align: right; font-weight: 600; color: var(--result); }
    .empty { color: var(--text-muted); font-size: .9rem; text-align: center; padding: 20px 0; }

    @media (max-width: 400px) {
      .key { height: 52px; font-size: 1rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Math Calculator</h1>
      <button class="theme-toggle" id="themeToggle">Light mode</button>
    </div>
    <div class="card">
      <div class="display">
        <div class="display-expr" id="displayExpr"></div>
        <div class="display-val" id="displayVal">0</div>
      </div>
      <div class="presets" id="presets"></div>
      <div class="keypad">
        <button class="key key-clear" data-key="C">C</button>
        <button class="key key-digit" data-key=".">.</button>
        <button class="key key-digit" data-key="⌫">⌫</button>
        <button class="key key-op"   data-key="/">÷</button>

        <button class="key key-digit" data-key="7">7</button>
        <button class="key key-digit" data-key="8">8</button>
        <button class="key key-digit" data-key="9">9</button>
        <button class="key key-op"   data-key="*">×</button>

        <button class="key key-digit" data-key="4">4</button>
        <button class="key key-digit" data-key="5">5</button>
        <button class="key key-digit" data-key="6">6</button>
        <button class="key key-op"   data-key="-">−</button>

        <button class="key key-digit" data-key="1">1</button>
        <button class="key key-digit" data-key="2">2</button>
        <button class="key key-digit" data-key="3">3</button>
        <button class="key key-op"   data-key="+">+</button>

        <button class="key key-digit key-zero" data-key="0">0</button>
        <button class="key key-eq"   data-key="=" colspan="2">=</button>
      </div>
      <div class="error" id="error"></div>
    </div>
    <div class="card">
      <h2>History</h2>
      <table>
        <thead><tr><th>Equation</th><th>Result</th></tr></thead>
        <tbody id="historyBody">
          <tr><td colspan="2" class="empty">No calculations yet.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <script>
    // ── Theme ──────────────────────────────────────────────────────────────
    const toggle = document.getElementById('themeToggle');
    function applyTheme(light) {
      document.body.classList.toggle('light', light);
      toggle.textContent = light ? 'Dark mode' : 'Light mode';
    }
    applyTheme(localStorage.getItem('theme') === 'light');
    toggle.addEventListener('click', () => {
      const isLight = document.body.classList.contains('light');
      applyTheme(!isLight);
      localStorage.setItem('theme', !isLight ? 'light' : 'dark');
    });

    // ── Presets ────────────────────────────────────────────────────────────
    const PRESETS = ['12 * 3', '100 / 4', '7 + 8', '50 - 13', '9 * 9', '144 / 12'];
    const presetsEl = document.getElementById('presets');
    PRESETS.forEach(p => {
      const btn = document.createElement('button');
      btn.className = 'preset-btn';
      btn.textContent = p;
      btn.addEventListener('click', () => evaluate(p));
      presetsEl.appendChild(btn);
    });

    // ── Calculator state ───────────────────────────────────────────────────
    // States: 'num1' | 'op' | 'num2' | 'result' | 'error'
    let num1 = '', op = '', num2 = '', state = 'num1';

    const exprEl  = document.getElementById('displayExpr');
    const valEl   = document.getElementById('displayVal');
    const errorEl = document.getElementById('error');

    function updateDisplay() {
      exprEl.textContent = op ? `${num1} ${op}` : '';
      if (state === 'num1')   valEl.textContent = num1 || '0';
      else if (state === 'op') valEl.textContent = num1;
      else                     valEl.textContent = num2 || '0';
    }

    function reset() {
      num1 = ''; op = ''; num2 = ''; state = 'num1';
      errorEl.textContent = '';
      updateDisplay();
    }

    function appendDigit(d) {
      errorEl.textContent = '';
      if (state === 'result' || state === 'error') {
        num1 = ''; op = ''; num2 = ''; state = 'num1';
      }
      if (state === 'num1') {
        if (d === '.' && num1.includes('.')) return;
        if (d === '.' && num1 === '') num1 = '0';
        num1 += d;
      } else {
        if (d === '.' && num2.includes('.')) return;
        if (d === '.' && num2 === '') num2 = '0';
        num2 += d;
        state = 'num2';
      }
      updateDisplay();
    }

    function appendOp(o) {
      errorEl.textContent = '';
      if (state === 'num1' && num1 === '') return;
      if (state === 'num2' && num2 !== '') {
        // chain: evaluate first then set new op
        submitEquation(`${num1} ${op} ${num2}`).then(result => {
          if (result !== null) { num1 = result; num2 = ''; op = o; state = 'op'; updateDisplay(); }
        });
        return;
      }
      op = o; state = 'op'; updateDisplay();
    }

    function backspace() {
      if (state === 'result' || state === 'error') { reset(); return; }
      if (state === 'num2' || state === 'op') {
        if (num2.length > 0) { num2 = num2.slice(0, -1); if (num2 === '') state = 'op'; }
        else { op = ''; state = 'num1'; }
      } else {
        num1 = num1.slice(0, -1);
      }
      updateDisplay();
    }

    async function submitEquation(eq) {
      const res = await fetch('/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({equation: eq}),
      });
      const data = await res.json();
      if (data.error) {
        errorEl.textContent = data.error;
        state = 'error';
        updateDisplay();
        return null;
      }
      return data.result;
    }

    async function pressEquals() {
      if (state !== 'num2' || num2 === '') { errorEl.textContent = 'Enter a complete equation first.'; return; }
      const eq = `${num1} ${op} ${num2}`;
      const result = await submitEquation(eq);
      if (result !== null) {
        exprEl.textContent = `${eq} =`;
        valEl.textContent = result;
        num1 = result; op = ''; num2 = ''; state = 'result';
        loadHistory();
      }
    }

    async function evaluate(eq) {
      const result = await submitEquation(eq);
      if (result !== null) {
        exprEl.textContent = `${eq} =`;
        valEl.textContent = result;
        num1 = result; op = ''; num2 = ''; state = 'result';
        loadHistory();
      }
    }

    // ── Keypad wiring ──────────────────────────────────────────────────────
    document.querySelectorAll('.key').forEach(btn => {
      btn.addEventListener('click', () => {
        const k = btn.dataset.key;
        if (k === 'C')  { reset(); return; }
        if (k === '⌫') { backspace(); return; }
        if (k === '=')  { pressEquals(); return; }
        if ('+-*/'.includes(k)) { appendOp(k); return; }
        appendDigit(k);
      });
    });

    // ── History ────────────────────────────────────────────────────────────
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
