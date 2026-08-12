"use client";

import { useEffect, useState } from "react";
import type { DailySummaryResponse, DashboardStats } from "@/types";

const API = "";

const STAGE_LABELS: Record<string, string> = {
  embryo: "עובר", infant: "יונק", child: "ילד", adult: "בוגר",
  first_woman: "אישה ראשונה", primary_woman: "אישה עיקרית",
  third_woman: "אישה שלישית", courtship: "חיזור",
  marriage: "נישואין", new_generation: "דור חדש",
};

const STAGE_EMOJIS: Record<string, string> = {
  embryo: "🥒", infant: "👶", child: "🧒", adult: "🧑",
  first_woman: "💕", primary_woman: "💍", third_woman: "🌟",
  courtship: "💐", marriage: "🤝", new_generation: "🌱",
};

const EVENT_LABELS: Record<string, string> = {
  war: "מלחמה", peace: "שלום", alliance: "ברית", economy: "כלכלה",
  immigration: "הגירה", technology: "טכנולוגיה", family: "משפחה",
  elections: "בחירות", threat: "איום", defense: "הגנה",
  diplomacy: "דיפלומטיה", terrorism: "טרור", security: "ביטחון",
  education: "חינוך", health: "בריאות", birth: "ילודה",
  demography: "דמוגרפיה", energy: "אנרגיה", food: "מזון",
  water: "מים", infrastructure: "תשתיות", science: "מדע",
  culture: "תרבות", religion: "דת", law: "משפט",
  protest: "מחאה", leadership: "מנהיגות", negotiation: "משא ומתן",
  refugees: "פליטים", innovation: "חדשנות", labor: "שוק העבודה",
  cooperation: "שיתוף פעולה", crisis: "משבר", recovery: "התאוששות",
  social_change: "שינוי חברתי",
};

export default function SynthesisPage() {
  const [summary, setSummary] = useState<DailySummaryResponse | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [sumRes, dashRes] = await Promise.all([
          fetch(`${API}/api/daily-summary`),
          fetch(`${API}/api/dashboard`),
        ]);
        const dashData = await dashRes.json();
        setStats(dashData);

        const sumText = await sumRes.text();
        if (sumText && sumText !== "null") {
          setSummary(JSON.parse(sumText));
        }
        setError(null);
      } catch {
        setError("שגיאה בטעינת הסיכום היומי");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">🧬</div>
          <div className="text-lg">טוען סיכום יומי...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">סיכום יומי</h1>
        <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
          סינתזה יומית של ניתוח חדשות התפתחותי
        </p>
      </header>

      {error && (
        <div
          className="rounded-xl p-4"
          style={{ background: "var(--card)", border: "1px solid var(--destructive)" }}
        >
          <span style={{ color: "var(--destructive)" }}>{error}</span>
        </div>
      )}

      {!summary && !error && (
        <div
          className="rounded-xl p-8 text-center"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <div className="text-4xl mb-4">📋</div>
          <h2 className="text-xl font-bold mb-2">אין סיכום יומי עדיין</h2>
          <p style={{ color: "var(--muted-foreground)" }}>
            הסיכום היומי נוצר אוטומטית בשעה 18:00 (שעון ישראל) או באמצעות הפעלה ידנית.
          </p>
        </div>
      )}

      {summary && (
        <>
          <div
            className="rounded-xl p-6"
            style={{ background: "var(--card)", border: "1px solid var(--border)" }}
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">📊</span>
              <div>
                <h2 className="text-xl font-bold">
                  סיכום ליום {new Date(summary.summary_date).toLocaleDateString("he-IL")}
                </h2>
                <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                  {summary.telegram_sent ? "✅ נשלח לטלגרם" : "⏳ טרם נשלח לטלגרם"}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatBox label="סה״כ אירועים" value={summary.total_articles} icon="📰" />
              <StatBox label="עולמי" value={summary.global_articles} icon="🌍" />
              <StatBox label="ישראלי" value={summary.israel_articles} icon="🇮🇱" />
              <StatBox
                label="רמת ודאות"
                value={`${(summary.confidence * 100).toFixed(0)}%`}
                icon="🔬"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <h3 className="text-lg font-bold mb-4">📈 שלב דומיננטי</h3>
              {summary.dominant_stage && (
                <div className="flex items-center gap-4 mb-4">
                  <span className="text-5xl">
                    {STAGE_EMOJIS[summary.dominant_stage] || "🧬"}
                  </span>
                  <div>
                    <div className="text-2xl font-bold">
                      {STAGE_LABELS[summary.dominant_stage] || summary.dominant_stage}
                    </div>
                    <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                      שלב ראשי
                    </div>
                  </div>
                </div>
              )}
              {summary.secondary_stage && (
                <div className="flex items-center gap-4">
                  <span className="text-3xl">
                    {STAGE_EMOJIS[summary.secondary_stage] || "🧬"}
                  </span>
                  <div>
                    <div className="text-lg font-semibold">
                      {STAGE_LABELS[summary.secondary_stage] || summary.secondary_stage}
                    </div>
                    <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                      שלב משני
                    </div>
                  </div>
                </div>
              )}
            </div>

            {stats && (
              <div
                className="rounded-xl p-6"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
              >
                <h3 className="text-lg font-bold mb-4">🎯 התפלגות סוגי אירועים</h3>
                <div className="space-y-2">
                  {Object.entries(stats.event_type_distribution)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 8)
                    .map(([type, count]) => {
                      const total = stats.total_articles_today || 1;
                      const pct = ((count / total) * 100).toFixed(0);
                      return (
                        <div key={type} className="flex items-center gap-2">
                          <div className="w-24 text-sm truncate">{EVENT_LABELS[type] || type}</div>
                          <div
                            className="flex-1 h-5 rounded-full overflow-hidden"
                            style={{ background: "var(--muted)" }}
                          >
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${Math.max(8, (count / total) * 100)}%`,
                                background: "var(--primary)",
                              }}
                            />
                          </div>
                          <div className="w-16 text-sm text-left">
                            {count} ({pct}%)
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>

          {summary.trend_text && (
            <div
              className="rounded-xl p-6"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <h3 className="text-lg font-bold mb-4">📝 ניתוח מגמות</h3>
              <div
                className="whitespace-pre-wrap leading-relaxed"
                style={{ color: "var(--foreground)" }}
              >
                {summary.trend_text}
              </div>
            </div>
          )}

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
        </>
      )}
    </div>
  );
}

function StatBox({
  label,
  value,
  icon,
}: {
  label: string;
  value: string | number;
  icon: string;
}) {
  return (
    <div
      className="rounded-lg p-4 text-center"
      style={{ background: "var(--muted)", border: "1px solid var(--border)" }}
    >
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>
        {label}
      </div>
    </div>
  );
}
