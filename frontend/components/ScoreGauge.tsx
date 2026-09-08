export function ScoreGauge({ score, label }: { score: number; label: string }) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "#16a34a" : score >= 50 ? "#d97706" : "#dc2626";

  return (
    <div className="card flex items-center gap-4">
      <svg width="96" height="96" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" />
        <circle
          cx="48"
          cy="48"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 48 48)"
        />
        <text x="48" y="54" textAnchor="middle" fontSize="22" fontWeight="600" fill="#0f172a">
          {score}
        </text>
      </svg>
      <div>
        <p className="text-sm font-medium text-ink">{label}</p>
        <p className="text-xs text-slate-500">out of 100</p>
      </div>
    </div>
  );
}
