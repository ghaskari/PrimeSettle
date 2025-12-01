import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def calculate_balances(transactions):
    df = pd.DataFrame(transactions, columns=["Debtor", "Creditor", "Amount"])

    people = pd.unique(df[["Debtor", "Creditor"]].values.ravel())
    balance = pd.Series(0.0, index=people)

    for _, row in df.iterrows():
        balance[row["Debtor"]] -= row["Amount"]
        balance[row["Creditor"]] += row["Amount"]

    df_balance = balance.reset_index()
    df_balance.columns = ["Name", "FinalBalance"]
    return df_balance


def calculate_settlements(df_balance):
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
                "Amount": round(pay, 2)
            })

            debt_amount -= pay
            creditors[creditor] -= pay

    return pd.DataFrame(settlements)


def generate_settlement_qr(df_settlement):
    if df_settlement.empty:
        return None

    text_payload = "Final Settlements:\n\n"

    for _, row in df_settlement.iterrows():
        text_payload += f"{row['From']} ➝ {row['To']} : {row['Amount']}\n"

    qr = qrcode.make(text_payload)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return buffer.getvalue()


def generate_invoice_pdf(df_settlement, qr_image_bytes):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFont("Helvetica", 12)
    c.drawString(50, 800, "Settlement Invoice")

    y = 760
    for _, row in df_settlement.iterrows():
        line = f"{row['From']} ➝ {row['To']} : {row['Amount']}"
        c.drawString(50, y, line)
        y -= 20

    # Add QR to PDF
    qr_path = "qr_temp.png"
    with open(qr_path, "wb") as f:
        f.write(qr_image_bytes)

    c.drawImage(qr_path, 350, 650, width=150, height=150)
    c.drawString(350, 630, "Scan to share")

    c.save()
    buffer.seek(0)
    return buffer


def generate_balance_chart_with_qr(df_balance: pd.DataFrame, qr_bytes: bytes) -> bytes:
    import matplotlib.pyplot as plt
    from io import BytesIO
    import matplotlib.image as mpimg

    # Create main figure
    fig = plt.figure(figsize=(10, 5))

    ax_chart = fig.add_axes([0.05, 0.15, 0.55, 0.75])  # [left, bottom, width, height]

    if not df_balance.empty:
        ax_chart.bar(df_balance["Name"], df_balance["FinalBalance"])

    ax_chart.set_title("Final Balances")
    ax_chart.set_ylabel("Amount")
    ax_chart.set_xlabel("People")

    ax_qr = fig.add_axes([0.68, 0.20, 0.28, 0.60])
    qr_img = mpimg.imread(BytesIO(qr_bytes))
    ax_qr.imshow(qr_img)
    ax_qr.axis("off")
    ax_qr.set_title("Scan to Share")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    buffer.seek(0)

    return buffer.getvalue()


st.set_page_config(page_title="ClearLedger – Settlement System", layout="centered")
st.title("💸 ClearLedger — Smart Group Settlement")

st.write("Dynamic settlement with CSV export, QR sharing, PDF invoices & charts ✅")

if "transactions" not in st.session_state:
    st.session_state.transactions = []


st.subheader("➕ Add Transaction")

with st.form("transaction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        debtor = st.text_input("Debtor")
    with col2:
        creditor = st.text_input("Creditor")
    with col3:
        amount = st.number_input("Amount", min_value=0.0, step=1.0)

    if st.form_submit_button("✅ Add"):
        if debtor and creditor and amount > 0:
            st.session_state.transactions.append((debtor, creditor, amount))
            st.success("Transaction added ✅")
        else:
            st.error("All fields required!")

st.subheader("📄 Current Transactions")

if st.session_state.transactions:
    st.dataframe(pd.DataFrame(
        st.session_state.transactions,
        columns=["Debtor", "Creditor", "Amount"]
    ))
else:
    st.info("No transactions yet.")

st.subheader("🧮 Calculate")

if st.button("🚀 Calculate Final Results"):

    df_balance = calculate_balances(st.session_state.transactions)
    df_settlement = calculate_settlements(df_balance)

    st.subheader("✅ Final Balances")
    st.dataframe(df_balance)

    st.subheader("✅ Final Settlements")
    st.dataframe(df_settlement)

    # ✅ Generate QR
    qr_bytes = generate_settlement_qr(df_settlement)

    st.subheader("📱 Share via QR")
    st.image(qr_bytes, width=250)

    # ✅ Generate Invoice PDF
    pdf_buffer = generate_invoice_pdf(df_settlement, qr_bytes)

    st.download_button(
        "🧾 Download Invoice PDF",
        pdf_buffer,
        file_name="settlement_invoice.pdf"
    )

    # ✅ Generate Chart with QR
    chart_buffer = generate_balance_chart_with_qr(df_balance, qr_bytes)

    st.subheader("📊 Balances Chart with QR")
    st.image(chart_buffer)

    st.download_button(
        "📊 Download Chart Image",
        chart_buffer,
        file_name="balances_chart_qr.png"
    )


if st.button("🔄 Reset All"):
    st.session_state.transactions = []
    st.rerun()
