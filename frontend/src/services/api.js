export async function predict(transaction) {
  const response = await fetch("http://localhost:8000/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(transaction) });
  return response.json();
}
