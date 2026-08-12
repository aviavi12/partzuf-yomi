"use client";

import { useState } from "react";
import Link from "next/link";
import type { NewsArticle, FullAnalysis } from "@/types";

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

const STAGE_LABELS: Record<string, string> = {
  embryo: "עובר", infant: "יונק", child: "ילד", adult: "בוגר",
  first_woman: "אישה ראשונה", primary_woman: "אישה עיקרית",
  third_woman: "אישה שלישית", courtship: "חיזור",
  marriage: "נישואין", new_generation: "דור חדש",
};

const RELEVANCE_LABELS: Record<string, string> = {
  direct: "ישיר", indirect: "עקיף", speculative: "השערתי", none: "אין",
};

interface Props {
  articles: NewsArticle[];
}

export default function NewsFeed({ articles }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadAnalysis(id: string) {
    if (selectedId === id) {
      setSelectedId(null);
      setAnalysis(null);
      return;
    }
    setSelectedId(id);
    setLoading(true);
    try {
      const res = await fetch(`/api/analysis/${id}`);
      const data = await res.json();
      setAnalysis(data);
    } catch {
      setAnalysis(null);
    }
    setLoading(false);
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-bold">עדכון חדשות</h3>
      {articles.map((article) => (
        <div key={article.id}>
          <div
            className="rounded-xl p-4 cursor-pointer transition-all hover:shadow-md"
            style={{
              background: "var(--card)",
              border: selectedId === article.id ? "2px solid var(--primary)" : "1px solid var(--border)",
            }}
            onClick={() => loadAnalysis(article.id)}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-base leading-relaxed">{article.headline}</h4>
                {article.summary && (
                  <p className="text-sm mt-1" style={{ color: "var(--muted-foreground)" }}>
                    {article.summary.slice(0, 150)}...
                  </p>
                )}
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ background: "var(--accent)", color: "var(--accent-foreground)" }}
                >
                  {article.source_name || "—"}
                </span>
                {article.is_demo && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                    DEMO
                  </span>
                )}
              </div>
            </div>
            <div className="flex gap-2 mt-2 text-xs" style={{ color: "var(--muted-foreground)" }}>
              {article.published_at && (
                <span>
                  {new Date(article.published_at).toLocaleString("he-IL", {
                    hour: "2-digit",
                    minute: "2-digit",
                    day: "2-digit",
                    month: "2-digit",
                  })}
                </span>
              )}
              <span>•</span>
              <span>{article.language === "he" ? "עברית" : "אנגלית"}</span>
            </div>
          </div>

          {selectedId === article.id && (
            <div
              className="rounded-xl p-4 mt-1 mx-2"
              style={{
                background: "var(--muted)",
                border: "1px solid var(--border)",
              }}
            >
              {loading ? (
                <div className="text-center py-4" style={{ color: "var(--muted-foreground)" }}>
                  טוען ניתוח...
                </div>
              ) : analysis ? (
                <div className="space-y-3 text-sm">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <InfoBox label="סוג אירוע" value={analysis.event_type_label_he || EVENT_LABELS[analysis.event_type || ""] || "—"} />
                    <InfoBox label="שלב התפתחותי" value={analysis.stage_label_he || STAGE_LABELS[analysis.developmental_stage || ""] || "—"} />
                    <InfoBox label="קשר לישראל" value={RELEVANCE_LABELS[analysis.israel_relevance_type || ""] || "—"} />
                    <InfoBox label="ודאות" value={`${(analysis.confidence * 100).toFixed(0)}%`} />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg p-3" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
                      <div className="font-semibold mb-1">👩 שכבת האם ({analysis.mother_analogy_score}/100)</div>
                      <p style={{ color: "var(--muted-foreground)" }}>{analysis.mother_analogy_text || "—"}</p>
                    </div>
                    <div className="rounded-lg p-3" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
                      <div className="font-semibold mb-1">👨 שכבת האב ({analysis.father_analogy_score}/100)</div>
                      <p style={{ color: "var(--muted-foreground)" }}>{analysis.father_analogy_text || "—"}</p>
                    </div>
                  </div>

                  {analysis.son_perspective && (
                    <div className="rounded-lg p-3" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
                      <div className="font-semibold mb-1">👦 נקודת המבט של הבן</div>
                      <p style={{ color: "var(--muted-foreground)" }}>{analysis.son_perspective.what_can_be_perceived}</p>
                      <p className="mt-1 italic text-xs" style={{ color: "var(--muted-foreground)" }}>
                        {analysis.son_perspective.developmental_meaning}
                      </p>
                    </div>
                  )}

                  {analysis.scientific_context && (
                    <div className="rounded-lg p-3 text-xs" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
                      <div className="font-semibold mb-1">
                        🔬 הקשר מדעי (רמה: {analysis.scientific_context.evidence_level})
                      </div>
                      <p style={{ color: "var(--muted-foreground)" }}>{analysis.scientific_context.text}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="text-xs italic" style={{ color: "var(--muted-foreground)" }}>
                      ⚠️ זהו מודל אנליטי מטפורי — אין לראות בו קביעה מדעית או רפואית.
                      סוג הטענה: {analysis.claim_type}
                    </div>
                    <Link
                      href={`/article/${article.id}`}
                      className="px-3 py-1 rounded-lg text-xs font-medium shrink-0"
                      style={{ background: "var(--primary)", color: "var(--primary-foreground)" }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      ניתוח מלא
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4" style={{ color: "var(--muted-foreground)" }}>
                  אין ניתוח זמין
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function InfoBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg p-2 text-center" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
      <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>{label}</div>
      <div className="font-bold mt-0.5">{value}</div>
    </div>
  );
}
