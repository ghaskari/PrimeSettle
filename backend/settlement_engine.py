# backend/settlement_engine.py
import pandas as pd
import qrcode
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def calculate_balances(transactions):
    """
    transactions: list of dicts like:
      {"debtor": "...", "creditor": "...", "amount": 123}
    """
    if not transactions:
        return pd.DataFrame(columns=["Name", "FinalBalance"])

    df = pd.DataFrame(transactions)
    df.columns = ["Debtor", "Creditor", "Amount"]

    people = pd.unique(df[["Debtor", "Creditor"]].values.ravel())
    balance = pd.Series(0.0, index=people)

    for _, row in df.iterrows():
        balance[row["Debtor"]] -= float(row["Amount"])
        balance[row["Creditor"]] += float(row["Amount"])

    df_balance = balance.reset_index()
    df_balance.columns = ["Name", "FinalBalance"]
    return df_balance


def calculate_settlements(df_balance: pd.DataFrame) -> pd.DataFrame:
    if df_balance.empty:
        return pd.DataFrame(columns=["From", "To", "Amount"])

    balance = pd.Series(
        df_balance["FinalBalance"].values,
        index=df_balance["Name"]
    )

    debtors = balance[balance < 0].abs()
    creditors = balance[balance > 0]

    settlements = []

    for debtor, debt_amount in debtors.items():
        for creditor in creditors.index:
            if debt_amount <= 0:
                break
            if creditors[creditor] <= 0:
                continue

            pay = min(debt_amount, creditors[creditor])

            settlements.append({
                "From": debtor,
                "To": creditor,
                "Amount": round(float(pay), 2)
            })

            debt_amount -= pay
            creditors[creditor] -= pay

    return pd.DataFrame(settlements)


# ---------- QR + PDF + CHART helpers ----------

def settlements_text(df_settlement: pd.DataFrame) -> str:
    if df_settlement.empty:
        return "No settlements."
    lines = ["Final Settlements:", ""]
    for _, row in df_settlement.iterrows():
        lines.append(f"{row['From']} ➝ {row['To']} : {row['Amount']}")
    return "\n".join(lines)


def generate_settlement_qr_bytes(df_settlement: pd.DataFrame) -> bytes:
    text_payload = settlements_text(df_settlement)
    qr = qrcode.make(text_payload)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()


def generate_invoice_pdf_bytes(df_settlement: pd.DataFrame, qr_bytes: bytes) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Settlement Invoice")

    c.setFont("Helvetica", 12)
    y = 770
    for _, row in df_settlement.iterrows():
        line = f"{row['From']} ➝ {row['To']} : {row['Amount']}"
        c.drawString(50, y, line)
        y -= 20
        if y < 100:
            c.showPage()
            y = 800
            c.setFont("Helvetica", 12)

    # add QR
    qr_buf = BytesIO(qr_bytes)
    qr_path_like = qr_buf  # reportlab can take a file-like in newer versions
    c.drawImage(qr_path_like, 380, 650, width=150, height=150)
    c.drawString(380, 630, "Scan to share")

    c.save()
    buf.seek(0)
    return buf.getvalue()


def generate_balance_chart_with_qr_bytes(df_balance: pd.DataFrame, qr_bytes: bytes) -> bytes:
    fig, ax = plt.subplots()
    if not df_balance.empty:
        ax.bar(df_balance["Name"], df_balance["FinalBalance"])
    ax.set_title("Final Balances")
    ax.set_ylabel("Amount")

    # add QR to the figure
    qr_img = plt.imread(BytesIO(qr_bytes))
    fig.figimage(qr_img, xo=50, yo=50, alpha=0.9)

    buf = BytesIO()
    plt.savefig(buf, format="PNG", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
