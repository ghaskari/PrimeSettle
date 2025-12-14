import pandas as pd
import qrcode
from io import BytesIO
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def calculate_balances(transactions):
    if not transactions:
        return pd.DataFrame(columns=["Name", "FinalBalance"])

    df = pd.DataFrame(transactions)
    df.columns = ["Debtor", "Creditor", "Amount"]

    people = pd.unique(df[["Debtor", "Creditor"]].values.ravel())
    balance = pd.Series(0.0, index=people)

    for _, row in df.iterrows():
        balance[row["Debtor"]] -= row["Amount"]
        balance[row["Creditor"]] += row["Amount"]

    return balance.reset_index().rename(
        columns={"index": "Name", 0: "FinalBalance"}
    )


def calculate_settlements(df_balance):
    if df_balance.empty:
        return pd.DataFrame(columns=["From", "To", "Amount"])

    bal = pd.Series(df_balance.FinalBalance.values, index=df_balance.Name)
    debtors = bal[bal < 0].abs()
    creditors = bal[bal > 0]

    settlements = []

    for d, d_amt in debtors.items():
        for c in creditors.index:
            if d_amt <= 0:
                break
            if creditors[c] <= 0:
                continue

            pay = min(d_amt, creditors[c])
            settlements.append({"From": d, "To": c, "Amount": round(pay, 2)})
            d_amt -= pay
            creditors[c] -= pay

    return pd.DataFrame(settlements)


def generate_settlement_qr_bytes(df_settlement):
    if df_settlement.empty:
        text = "No settlements required."
    else:
        text = "\n".join(
            f"{r.From} ➝ {r.To} : {r.Amount}"
            for r in df_settlement.itertuples()
        )

    qr = qrcode.make(text)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()


def generate_invoice_pdf_bytes(df_settlement, qr_bytes):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Settlement Invoice")

    c.setFont("Helvetica", 12)
    y = 760

    for _, r in df_settlement.iterrows():
        c.drawString(50, y, f"{r.From} ➝ {r.To} : {r.Amount}")
        y -= 20
        if y < 120:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 780

    qr_image = ImageReader(BytesIO(qr_bytes))
    c.drawImage(qr_image, 380, 650, width=150, height=150)
    c.drawString(380, 630, "Scan to share")

    c.save()
    buf.seek(0)
    return buf.getvalue()


def generate_balance_chart_with_qr_bytes(df_balance, qr_bytes):
    import matplotlib.pyplot as plt
    from io import BytesIO

    fig, (ax_chart, ax_qr) = plt.subplots(
        1, 2, figsize=(8, 4),
        gridspec_kw={"width_ratios": [3, 1]}
    )

    # --- Bar chart
    if not df_balance.empty:
        ax_chart.bar(df_balance["Name"], df_balance["FinalBalance"])
    ax_chart.set_title("Final Balances")
    ax_chart.set_ylabel("Amount")
    ax_chart.grid(axis="y", alpha=0.3)

    # --- QR code panel
    qr_img = plt.imread(BytesIO(qr_bytes))
    ax_qr.imshow(qr_img)
    ax_qr.axis("off")
    ax_qr.set_title("Settlement QR", fontsize=10)

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="PNG", dpi=150)
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()
