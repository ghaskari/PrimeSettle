import React, { useState } from "react";

const API_BASE = "http://localhost:5000";

function App() {
  const [debtor, setDebtor] = useState("");
  const [creditor, setCreditor] = useState("");
  const [amount, setAmount] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [balances, setBalances] = useState([]);
  const [settlements, setSettlements] = useState([]);
  const [qrUrl, setQrUrl] = useState(null);
  const [chartUrl, setChartUrl] = useState(null);

  const addTransaction = () => {
    if (!debtor || !creditor || !amount) return;
    setTransactions(prev => [
      ...prev,
      { debtor, creditor, amount: parseFloat(amount) }
    ]);
    setDebtor("");
    setCreditor("");
    setAmount("");
  };

  const calculate = async () => {
    const res = await fetch(`${API_BASE}/api/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions })
    });
    const data = await res.json();
    setBalances(data.balances || []);
    setSettlements(data.settlements || []);
  };

  const fetchBlobAsUrl = async (path) => {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions })
    });
    const blob = await res.blob();
    return URL.createObjectURL(blob);
  };

  const showQr = async () => {
    const url = await fetchBlobAsUrl("/api/qr");
    setQrUrl(url);
  };

  const showChart = async () => {
    const url = await fetchBlobAsUrl("/api/balance-chart");
    setChartUrl(url);
  };

  const downloadInvoice = async () => {
    const res = await fetch(`${API_BASE}/api/invoice-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions })
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "settlement_invoice.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  const resetAll = () => {
    setTransactions([]);
    setBalances([]);
    setSettlements([]);
    setQrUrl(null);
    setChartUrl(null);
  };

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", fontFamily: "sans-serif" }}>
      <h1>💸 ClearLedger — React UI</h1>

      <h2>Add Transaction</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <input
          placeholder="Debtor"
          value={debtor}
          onChange={e => setDebtor(e.target.value)}
        />
        <input
          placeholder="Creditor"
          value={creditor}
          onChange={e => setCreditor(e.target.value)}
        />
        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />
        <button onClick={addTransaction}>Add</button>
      </div>

      <h2>Transactions</h2>
      <table border="1" cellPadding="4" cellSpacing="0" width="100%">
        <thead>
          <tr>
            <th>Debtor</th>
            <th>Creditor</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, i) => (
            <tr key={i}>
              <td>{tx.debtor}</td>
              <td>{tx.creditor}</td>
              <td>{tx.amount}</td>
            </tr>
          ))}
          {transactions.length === 0 && (
            <tr><td colSpan={3}>No transactions yet</td></tr>
          )}
        </tbody>
      </table>

      <div style={{ marginTop: 10 }}>
        <button onClick={calculate}>Calculate</button>
        <button onClick={resetAll} style={{ marginLeft: 8 }}>Reset</button>
      </div>

      <h2>Balances</h2>
      <table border="1" cellPadding="4" cellSpacing="0" width="100%">
        <thead>
          <tr><th>Name</th><th>Final Balance</th></tr>
        </thead>
        <tbody>
          {balances.map((b, i) => (
            <tr key={i}>
              <td>{b.name}</td>
              <td>{b.finalBalance}</td>
            </tr>
          ))}
          {balances.length === 0 && (
            <tr><td colSpan={2}>No balances yet</td></tr>
          )}
        </tbody>
      </table>

      <h2>Settlements</h2>
      <table border="1" cellPadding="4" cellSpacing="0" width="100%">
        <thead>
          <tr><th>From</th><th>To</th><th>Amount</th></tr>
        </thead>
        <tbody>
          {settlements.map((s, i) => (
            <tr key={i}>
              <td>{s.from}</td>
              <td>{s.to}</td>
              <td>{s.amount}</td>
            </tr>
          ))}
          {settlements.length === 0 && (
            <tr><td colSpan={3}>No settlements yet</td></tr>
          )}
        </tbody>
      </table>

      <h2>QR & Exports</h2>
      <button onClick={showQr}>Show QR</button>
      <button onClick={downloadInvoice} style={{ marginLeft: 8 }}>
        Download Invoice PDF
      </button>
      <button onClick={showChart} style={{ marginLeft: 8 }}>
        Show Chart
      </button>

      {qrUrl && (
        <div style={{ marginTop: 10 }}>
          <h3>QR</h3>
          <img src={qrUrl} alt="QR" width={200} />
        </div>
      )}

      {chartUrl && (
        <div style={{ marginTop: 10 }}>
          <h3>Balance Chart</h3>
          <img src={chartUrl} alt="Chart" width={400} />
        </div>
      )}
    </div>
  );
}

export default App;
