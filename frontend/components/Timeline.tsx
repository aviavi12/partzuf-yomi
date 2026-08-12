"use client";

const STAGES = [
  { key: "embryo", label: "עובר", emoji: "🥒", color: "#ef4444" },
  { key: "infant", label: "יונק", emoji: "👶", color: "#f97316" },
  { key: "child", label: "ילד", emoji: "🧒", color: "#eab308" },
  { key: "adult", label: "בוגר", emoji: "🧑", color: "#22c55e" },
  { key: "first_woman", label: "אישה ראשונה", emoji: "💕", color: "#ec4899" },
  { key: "primary_woman", label: "אישה עיקרית", emoji: "💍", color: "#a855f7" },
  { key: "third_woman", label: "אישה שלישית", emoji: "🌟", color: "#6366f1" },
  { key: "courtship", label: "חיזור", emoji: "💐", color: "#3b82f6" },
  { key: "marriage", label: "נישואין", emoji: "🤝", color: "#14b8a6" },
  { key: "new_generation", label: "דור חדש", emoji: "🌱", color: "#06b6d4" },
];

interface Props {
  distribution: Record<string, number>;
}

export default function Timeline({ distribution }: Props) {
  const total = Object.values(distribution).reduce((a, b) => a + b, 0) || 1;

  return (
    <div
      className="rounded-xl p-4"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <h3 className="text-lg font-bold mb-4">ציר זמן התפתחותי</h3>
      <div className="space-y-3">
        {STAGES.map((stage, i) => {
          const count = distribution[stage.key] || 0;
          const pct = ((count / total) * 100).toFixed(0);
          return (
            <div key={stage.key} className="flex items-center gap-3">
              <div className="w-8 text-center text-xl">{stage.emoji}</div>
              <div className="w-28 text-sm font-medium">{stage.label}</div>
              <div className="flex-1 h-6 rounded-full overflow-hidden" style={{ background: "var(--muted)" }}>
                <div
                  className="h-full rounded-full transition-all duration-500 flex items-center justify-end px-2"
                  style={{
                    width: `${Math.max(count > 0 ? 8 : 0, (count / total) * 100)}%`,
                    background: stage.color,
                  }}
                >
                  {count > 0 && (
                    <span className="text-xs text-white font-bold">{count}</span>
                  )}
                </div>
              </div>
              <div className="w-12 text-left text-sm" style={{ color: "var(--muted-foreground)" }}>
                {pct}%
              </div>
              {i < STAGES.length - 1 && (
                <div className="absolute" style={{ display: "none" }}>↓</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
