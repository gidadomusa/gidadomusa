import { useState } from "react";

const initialTransaction = {
  amount: 850,
  hour: 2,
  distance_from_home_km: 300,
  recent_transaction_count: 8,
};

function App() {
  const [transaction, setTransaction] = useState(initialTransaction);
  const [result, setResult] = useState(null);

  function updateField(event) {
    setTransaction({ ...transaction, [event.target.name]: Number(event.target.value) });
  }

  async function submit(event) {
    event.preventDefault();
    const response = await fetch("http://localhost:8000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(transaction),
    });
    setResult(await response.json());
  }

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Risk intelligence / v0.1</p>
        <h1>Explain the signal before you act.</h1>
        <p className="lede">A transparent transaction review workspace for financial-risk teams.</p>
      </header>
      <section className="workspace">
        <form onSubmit={submit}>
          <h2>Transaction review</h2>
          {Object.entries(transaction).map(([name, value]) => (
            <label key={name}>
              {name.replaceAll("_", " ")}
              <input name={name} type="number" value={value} onChange={updateField} min="0" />
            </label>
          ))}
          <button type="submit">Run risk assessment</button>
        </form>
        <section className="result" aria-live="polite">
          <p className="eyebrow">Assessment</p>
          {result ? (
            <>
              <strong className={result.risk_label}>{result.risk_label} risk</strong>
              <p className="score">{Math.round(result.risk_score * 100)}<span>/100</span></p>
              <h2>Why this result?</h2>
              {result.explanations.map((item) => (
                <div className="explanation" key={item.feature}>
                  <span>{item.feature.replaceAll("_", " ")}</span>
                  <b>{item.impact.toFixed(2)}</b>
                </div>
              ))}
            </>
          ) : <p className="empty">Submit a transaction to see its risk score and contributing signals.</p>}
        </section>
      </section>
    </main>
  );
}

export default App;