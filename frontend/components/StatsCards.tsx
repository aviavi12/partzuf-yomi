"use client";

import type { DashboardStats } from "@/types";

interface Props {
  stats: DashboardStats;
}

export default function StatsCards({ stats }: Props) {
  const cards = [
    { label: "סה\"כ חדשות היום", value: stats.total_articles_today, icon: "📰" },
    { label: "חדשות עולמיות", value: stats.global_articles_today, icon: "🌍" },
    { label: "חדשות ישראליות", value: stats.israel_articles_today, icon: "🇮🇱" },
    { label: "קשר ממוצע לישראל", value: `${stats.avg_israel_relevance}%`, icon: "🔗" },
    { label: "שלב דומיננטי", value: stats.dominant_stage_label_he || "—", icon: "🧬" },
    { label: "ודאות ממוצעת", value: `${(stats.avg_confidence * 100).toFixed(0)}%`, icon: "🎯" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl p-4"
          style={{
            background: "var(--card)",
            color: "var(--card-foreground)",
            border: "1px solid var(--border)",
          }}
        >
          <div className="text-2xl mb-2">{card.icon}</div>
          <div className="text-2xl font-bold">{card.value}</div>
          <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
            {card.label}
          </div>
        </div>
      ))}
    </div>
  );
}
