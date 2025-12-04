from flask import Flask, request, jsonify, send_file, render_template_string
from io import BytesIO
from settlement_engine import (
    calculate_balances,
    calculate_settlements,
    generate_settlement_qr_bytes,
    generate_invoice_pdf_bytes,
    generate_balance_chart_with_qr_bytes,
)

app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>PrimeSettle — Fast, Fair, Final</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 30px auto; }
        input, button { padding: 6px 10px; margin: 4px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #aaa; padding: 6px; text-align: left; }
        img { margin-top: 15px; }
    </style>
</head>
<body>

<h1>💸 PrimeSettle — Fast, Fair, Final</h1>

<h3>Add Transaction</h3>
<input id="debtor" placeholder="Debtor">
<input id="creditor" placeholder="Creditor">
<input id="amount" type="number" placeholder="Amount">
<button onclick="addTx()">Add</button>

<h3>Transactions</h3>
<table>
<thead><tr><th>Debtor</th><th>Creditor</th><th>Amount</th></tr></thead>
<tbody id="tx"></tbody>
</table>

<br>
<button onclick="calculate()">🚀 Calculate</button>
<button onclick="resetAll()">🔄 Reset</button>

<h3>Balances</h3>
<table>
<thead><tr><th>Name</th><th>Final Balance</th></tr></thead>
<tbody id="balances"></tbody>
</table>

<h3>Settlements</h3>
<table>
<thead><tr><th>From</th><th>To</th><th>Amount</th></tr></thead>
<tbody id="settlements"></tbody>
</table>

<h3>Exports</h3>
<button onclick="showQR()">Show QR</button>
<button onclick="downloadPDF()">Download Invoice PDF</button>
<button onclick="showChart()">Show Balance Chart</button>

<div id="qr"></div>
<div id="chart"></div>

<script>
let transactions = [];

function addTx() {
    const d = debtor.value.trim();
    const c = creditor.value.trim();
    const a = parseFloat(amount.value);

    if (!d || !c || !a) return alert("Fill all fields!");

    transactions.push({debtor: d, creditor: c, amount: a});
    renderTx();
    debtor.value = ""; creditor.value = ""; amount.value = "";
}

function renderTx() {
    tx.innerHTML = "";
    transactions.forEach(t => {
        tx.innerHTML += `<tr><td>${t.debtor}</td><td>${t.creditor}</td><td>${t.amount}</td></tr>`;
    });
}

async function calculate() {
    const res = await fetch("/api/calculate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({transactions})
    });
    const data = await res.json();

    balances.innerHTML = "";
    settlements.innerHTML = "";

    data.balances.forEach(b => {
        balances.innerHTML += `<tr><td>${b.name}</td><td>${b.finalBalance}</td></tr>`;
    });

    data.settlements.forEach(s => {
        settlements.innerHTML += `<tr><td>${s.from}</td><td>${s.to}</td><td>${s.amount}</td></tr>`;
    });
}

async function showQR() {
    const res = await fetch("/api/qr", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({transactions})
    });
    const blob = await res.blob();
    qr.innerHTML = `<img src="${URL.createObjectURL(blob)}" width="200">`;
}

async function downloadPDF() {
    const res = await fetch("/api/invoice-pdf", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({transactions})
    });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "settlement_invoice.pdf";
    a.click();
}

async function showChart() {
    const res = await fetch("/api/balance-chart", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({transactions})
    });
    const blob = await res.blob();
    chart.innerHTML = `<img src="${URL.createObjectURL(blob)}" width="400">`;
}

function resetAll() {
    transactions = [];
    tx.innerHTML = "";
    balances.innerHTML = "";
    settlements.innerHTML = "";
    qr.innerHTML = "";
    chart.innerHTML = "";
}
</script>

</body>
</html>
"""

@app.route("/")
def browser_ui():
    return render_template_string(HTML_UI)


def parse_transactions(json_data):
    tx_raw = json_data.get("transactions", [])
    transactions = []
    for item in tx_raw:
        transactions.append({
            "debtor": item["debtor"],
            "creditor": item["creditor"],
            "amount": float(item["amount"])
        })
    return transactions


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)

    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)

    return jsonify({
        "balances": df_balance.to_dict(orient="records"),
        "settlements": df_settlement.to_dict(orient="records")
    })


@app.route("/api/qr", methods=["POST"])
def api_qr():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)
    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)

    return send_file(BytesIO(qr_bytes), mimetype="image/png")


@app.route("/api/invoice-pdf", methods=["POST"])
def api_invoice_pdf():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)
    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)
    pdf_bytes = generate_invoice_pdf_bytes(df_settlement, qr_bytes)

    return send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True)


@app.route("/api/balance-chart", methods=["POST"])
def api_balance_chart():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)
    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)
    chart_bytes = generate_balance_chart_with_qr_bytes(df_balance, qr_bytes)

    return send_file(BytesIO(chart_bytes), mimetype="image/png")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
