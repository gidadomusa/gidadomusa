import { useState } from "react";

export function usePrediction() {
  const [result, setResult] = useState(null);
  return { result, setResult };
}
