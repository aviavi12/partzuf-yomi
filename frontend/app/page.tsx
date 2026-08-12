"use client";

import { useEffect, useState, useCallback } from "react";
import StatsCards from "@/components/StatsCards";
import StageChart from "@/components/StageChart";
import NewsFeed from "@/components/NewsFeed";
import Timeline from "@/components/Timeline";
import EventFilter from "@/components/EventFilter";
import type { DashboardStats, NewsArticle } from "@/types";

const API = "http://localhost:8000";

export default function Home() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [sourceFilter, setSourceFilter] = useState("all");
  const [eventFilter, setEventFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"feed" | "timeline">("feed");

  const loadArticles = useCallback(async (source: string, eventType: string | null) => {
    const params = new URLSearchParams({ page_size: "50" });
    if (source === "world") params.set("source", "ap");
    if (source === "israel") params.set("source", "rotter");
    if (eventType) params.set("event_type", eventType);
    const res = await fetch(`${API}/api/news?${params}`);
    const data = await res.json();
    return data.items || [];
  }, []);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [dashRes, items] = await Promise.all([
          fetch(`${API}/api/dashboard`).then((r) => r.json()),
          loadArticles("all", null),
        ]);
        setStats(dashRes);
        setArticles(items);
        setError(null);
      } catch {
        setError("שגיאה בחיבור לשרת. ודא שה-backend פועל על http://localhost:8000");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [loadArticles]);

  async function handleSourceFilter(key: string) {
    setSourceFilter(key);
    try {
      const items = await loadArticles(key, eventFilter);
      setArticles(items);
    } catch { /* keep current */ }
  }

  async function handleEventFilter(type: string | null) {
    setEventFilter(type);
    try {
      const items = await loadArticles(sourceFilter, type);
      setArticles(items);
    } catch { /* keep current */ }
  }

  const sourceFilters = [
    { key: "all", label: "הכל" },
    { key: "world", label: "🌍 עולמי" },
    { key: "israel", label: "🇮🇱 ישראל" },
  ];

  const tabs = [
    { key: "feed" as const, label: "עדכונים" },
    { key: "timeline" as const, label: "ציר זמן" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">🧬</div>
          <div className="text-lg">טוען פרצוף יומי...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div
          className="text-center p-8 rounded-xl max-w-md"
          style={{ background: "var(--card)", border: "1px solid var(--destructive)" }}
        >
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-lg font-bold mb-2">שגיאה</div>
          <div style={{ color: "var(--muted-foreground)" }}>{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <header className="flex items-center justify-between">
        <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
          מנוע ניתוח חדשות התפתחותי — Israel News Developmental Analysis Engine
        </p>
        <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
          {new Date().toLocaleDateString("he-IL", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </div>
      </header>

      {stats && <StatsCards stats={stats} />}

      <div className="flex gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              background: tab === t.key ? "var(--primary)" : "var(--muted)",
              color: tab === t.key ? "var(--primary-foreground)" : "var(--foreground)",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "feed" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="flex gap-2 flex-wrap">
              {sourceFilters.map((f) => (
                <button
                  key={f.key}
                  onClick={() => handleSourceFilter(f.key)}
                  className="px-3 py-1.5 rounded-lg text-sm transition-colors"
                  style={{
                    background: sourceFilter === f.key ? "var(--accent)" : "var(--muted)",
                    color: sourceFilter === f.key ? "var(--accent-foreground)" : "var(--muted-foreground)",
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>
            {stats && (
              <EventFilter
                eventTypes={Object.keys(stats.event_type_distribution)}
                selected={eventFilter}
                onSelect={handleEventFilter}
              />
            )}
            <NewsFeed articles={articles} />
          </div>
          <div className="space-y-4">
            {stats && <StageChart distribution={stats.stage_distribution} />}
            <div
              className="rounded-xl p-4"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <h3 className="text-lg font-bold mb-3">קשר לישראל</h3>
              {stats &&
                Object.entries(stats.israel_relevance_distribution).map(([key, val]) => (
                  <div key={key} className="flex justify-between py-1">
                    <span>
                      {key === "direct" ? "🔵 ישיר" : key === "indirect" ? "🟡 עקיף" : "⚪ השערתי"}
                    </span>
                    <span className="font-bold">{val}</span>
                  </div>
                ))}
            </div>
            <div
              className="rounded-xl p-4 text-xs"
              style={{
                background: "var(--muted)",
                border: "1px solid var(--border)",
                color: "var(--muted-foreground)",
              }}
            >
              <p className="font-bold mb-1">⚠️ הערה חשובה</p>
              <p>
                מערכת זו משתמשת במודל התפתחותי כמסגרת אנליטית מטפורית.
                אין לראות בתוצאות קביעה מדעית, רפואית או פסיכולוגית.
                כל פרשנות מסומנת לפי רמת הוודאות שלה.
              </p>
            </div>
          </div>
        </div>
      ) : (
        stats && <Timeline distribution={stats.stage_distribution} />
      )}
    </div>
  );
}
