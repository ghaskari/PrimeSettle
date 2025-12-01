from flask import Flask, request, jsonify, send_file
from io import BytesIO
from settlement_engine import (
    calculate_balances,
    calculate_settlements,
    generate_settlement_qr_bytes,
    generate_invoice_pdf_bytes,
    generate_balance_chart_with_qr_bytes,
)

app = Flask(__name__)


def parse_transactions(json_data):
    tx_raw = json_data.get("transactions", [])
    transactions = []
    for item in tx_raw:
        debtor = item.get("debtor") or item.get("Debtor")
        creditor = item.get("creditor") or item.get("Creditor")
        amount = item.get("amount") or item.get("Amount")
        if debtor and creditor and amount is not None:
            transactions.append(
                {"debtor": debtor, "creditor": creditor, "amount": float(amount)}
            )
    return transactions


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)

    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)

    balances_json = [
        {"name": row["Name"], "finalBalance": row["FinalBalance"]}
        for _, row in df_balance.iterrows()
    ]

    settlements_json = [
        {"from": row["From"], "to": row["To"], "amount": row["Amount"]}
        for _, row in df_settlement.iterrows()
    ]

    return jsonify({
        "balances": balances_json,
        "settlements": settlements_json
    })


@app.route("/api/qr", methods=["POST"])
def api_qr():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)

    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)

    return send_file(
        BytesIO(qr_bytes),
        mimetype="image/png",
        as_attachment=False,
        download_name="settlements_qr.png"
    )


@app.route("/api/invoice-pdf", methods=["POST"])
def api_invoice_pdf():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)

    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)
    pdf_bytes = generate_invoice_pdf_bytes(df_settlement, qr_bytes)

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="settlement_invoice.pdf"
    )


@app.route("/api/balance-chart", methods=["POST"])
def api_balance_chart():
    data = request.get_json(force=True)
    transactions = parse_transactions(data)

    df_balance = calculate_balances(transactions)
    df_settlement = calculate_settlements(df_balance)
    qr_bytes = generate_settlement_qr_bytes(df_settlement)
    chart_bytes = generate_balance_chart_with_qr_bytes(df_balance, qr_bytes)

    return send_file(
        BytesIO(chart_bytes),
        mimetype="image/png",
        as_attachment=False,
        download_name="balances_chart_qr.png"
    )


if __name__ == "__main__":
    app.run(debug=True)
