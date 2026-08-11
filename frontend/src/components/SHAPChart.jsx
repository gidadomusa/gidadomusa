export default function SHAPChart({ explanations = [] }) { return <ul>{explanations.map((item) => <li key={item.feature}>{item.feature}: {item.impact}</li>)}</ul>; }
