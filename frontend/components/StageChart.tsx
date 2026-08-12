"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const STAGE_LABELS: Record<string, string> = {
  embryo: "עובר",
  infant: "יונק",
  child: "ילד",
  adult: "בוגר",
  first_woman: "אישה ראשונה",
  primary_woman: "אישה עיקרית",
  third_woman: "אישה שלישית",
  courtship: "חיזור",
  marriage: "נישואין",
  new_generation: "דור חדש",
};

const COLORS = [
  "#ef4444", "#f97316", "#eab308", "#22c55e", "#ec4899",
  "#a855f7", "#6366f1", "#3b82f6", "#14b8a6", "#06b6d4",
];

interface Props {
  distribution: Record<string, number>;
}

export default function StageChart({ distribution }: Props) {
  const stageOrder = [
    "embryo", "infant", "child", "adult", "first_woman",
    "primary_woman", "third_woman", "courtship", "marriage", "new_generation",
  ];

  const data = stageOrder.map((key, i) => ({
    name: STAGE_LABELS[key] || key,
    count: distribution[key] || 0,
    color: COLORS[i],
  }));

  return (
    <div
      className="rounded-xl p-4"
      style={{
        background: "var(--card)",
        border: "1px solid var(--border)",
      }}
    >
      <h3 className="text-lg font-bold mb-4">התפלגות שלבים התפתחותיים</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ right: 20, left: 100 }}>
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
