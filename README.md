# 💸 PrimeSettle

PrimeSettle is a smart **group expense settlement system** that calculates balances, generates optimal settlement payments, and provides **QR sharing, invoice PDF export, and balance charts with QR** — all running directly on a **Flask backend with a built-in browser UI**.

You do **NOT** need Streamlit or any frontend framework to use it.

---

## ✅ Features

* ✅ Add unlimited transactions between people
* ✅ Automatic final balance calculation
* ✅ Optimized settlement payments
* ✅ QR code for sharing settlements
* ✅ PDF invoice with embedded QR
* ✅ Balance chart with QR code
* ✅ Works directly in the browser (no frontend needed)
* ✅ REST API ready for mobile / React / Telegram bots
* ✅ No database required (stateless)

---

## 📂 Project Structure

```
PrimeSettle/
│
├── backend/
│   ├── app.py                # Flask backend + browser UI
│   └── settlement_engine.py # Core business logic (calculations, QR, PDF, charts)
│
├── app.py                    # Streamlit version (optional / legacy)
├── settlement_engine.py     # Streamlit engine (legacy)
├── requirements.txt
├── README.md
├── qr_temp.png               # Temporary QR file (auto-generated)
└── .gitignore
```

---

## ⚙️ Installation

### 1️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the App (NO Streamlit Required)

```bash
cd backend
python app.py
```

You should see:

```
Running on http://127.0.0.1:5000
```

---

## 🌐 Open in Browser

Open this URL:

```
http://127.0.0.1:5000
```

You will see the **PrimeSettle Web UI directly from Flask** where you can:

* ➕ Add Transactions
* 🧮 Calculate Final Results
* 📱 Generate QR for settlements
* 🧾 Download Invoice PDF
* 📊 Show Balance Chart with QR
* 🔄 Reset everything

---

## 🔌 REST API Endpoints

PrimeSettle can also be used as a pure backend:

| Feature       | Method | Endpoint             |
| ------------- | ------ | -------------------- |
| Calculate     | POST   | `/api/calculate`     |
| QR Image      | POST   | `/api/qr`            |
| Invoice PDF   | POST   | `/api/invoice-pdf`   |
| Balance Chart | POST   | `/api/balance-chart` |

---

## ✅ Request Format (JSON)

```json
{
  "transactions": [
    {"debtor": "Person1", "creditor": "Person2", "amount": 100},
    {"debtor": "Person3", "creditor": "Person1", "amount": 50}
  ]
}
```

---

## 🧪 Test With cURL

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"debtor": "Person1", "creditor": "Person2", "amount": 100},
      {"debtor": "Person3", "creditor": "Person1", "amount": 50}
    ]
  }'
```

---

## 📦 Output Examples

* ✅ Settlement QR image
* ✅ Invoice PDF with QR
* ✅ Balance Chart with QR
* ✅ JSON API responses for mobile / frontend apps

---

## 📜 License

MIT License — Free to use, modify, and distribute.
