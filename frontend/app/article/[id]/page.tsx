"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { FullAnalysis } from "@/types";

const API = "http://localhost:8000";

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

const STAGE_DESCRIPTIONS: Record<string, string> = {
  embryo: "שלב ראשוני — הישרדות, איומים קיומיים, משברים בסיסיים",
  infant: "שלב תינוקות — צרכים בסיסיים, טיפוח, בריאות ותזונה",
  child: "שלב ילדות — למידה, חינוך, חדשנות וגילוי",
  adult: "שלב בגרות — אחריות, ממשל, כלכלה ומשפט",
  first_woman: "אישה ראשונה — מפגש ראשוני, סקרנות, הכרה",
  primary_woman: "אישה עיקרית — שותפות, בריתות, שיתוף פעולה",
  third_woman: "אישה שלישית — מורכבות, ריבוי קשרים, ניואנסים",
  courtship: "חיזור — משא ומתן, דיפלומטיה, תהליכי הכרה",
  marriage: "נישואין — הסכמים, שלום, התחייבויות ארוכות טווח",
  new_generation: "דור חדש — ילודה, צמיחה דמוגרפית, עתיד",
};

const RELEVANCE_LABELS: Record<string, string> = {
  direct: "ישיר", indirect: "עקיף", speculative: "השערתי", none: "אין",
};

const CLAIM_LABELS: Record<string, string> = {
  fact: "עובדה", inference: "היסק", interpretation: "פרשנות",
  speculation: "השערה", metaphor: "מטפורה",
};

const EVIDENCE_LABELS: Record<string, string> = {
  established: "מבוסס", supported: "נתמך", plausible: "סביר",
  speculative: "השערתי", metaphorical: "מטפורי",
};

export default function ArticlePage() {
  const params = useParams();
  const id = params?.id as string;
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function load() {
      try {
        setLoading(true);
        const res = await fetch(`${API}/api/analysis/${id}`);
        if (!res.ok) throw new Error("Not found");
        setAnalysis(await res.json());
        setError(null);
      } catch {
        setError("לא נמצא ניתוח עבור כתבה זו");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-4xl mb-4">🧬</div>
          <div className="text-lg">טוען ניתוח...</div>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
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

  const stage = analysis.developmental_stage || "";

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {analysis.url && (
        <div className="flex justify-end">
          <a
            href={analysis.url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg text-sm"
            style={{ background: "var(--accent)", color: "var(--accent-foreground)" }}
          >
            מקור מקורי
          </a>
        </div>
      )}

      <div
        className="rounded-xl p-6"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
      >
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-2xl font-bold leading-relaxed">{analysis.headline}</h1>
          <span
            className="shrink-0 px-3 py-1 rounded-full text-sm"
            style={{ background: "var(--accent)", color: "var(--accent-foreground)" }}
          >
            {analysis.source_name || "—"}
          </span>
        </div>
        {analysis.published_at && (
          <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
            {new Date(analysis.published_at).toLocaleString("he-IL", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <InfoCard
          label="סוג אירוע"
          value={analysis.event_type_label_he || analysis.event_type || "—"}
          icon="🎯"
        />
        <InfoCard
          label="שלב התפתחותי"
          value={analysis.stage_label_he || STAGE_LABELS[stage] || "—"}
          icon={STAGE_EMOJIS[stage] || "🧬"}
        />
        <InfoCard
          label="קשר לישראל"
          value={RELEVANCE_LABELS[analysis.israel_relevance_type || ""] || "—"}
          icon={
            analysis.israel_relevance_type === "direct"
              ? "🔵"
              : analysis.israel_relevance_type === "indirect"
                ? "🟡"
                : "⚪"
          }
        />
        <InfoCard
          label="רמת ודאות"
          value={`${(analysis.confidence * 100).toFixed(0)}%`}
          icon="🔬"
        />
      </div>

      {stage && STAGE_DESCRIPTIONS[stage] && (
        <div
          className="rounded-xl p-4"
          style={{ background: "var(--accent)", border: "1px solid var(--border)" }}
        >
          <div className="flex items-center gap-3">
            <span className="text-3xl">{STAGE_EMOJIS[stage]}</span>
            <div>
              <div className="font-bold">
                {STAGE_LABELS[stage]} — שלב {(Object.keys(STAGE_LABELS).indexOf(stage) + 1)}/10
              </div>
              <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                {STAGE_DESCRIPTIONS[stage]}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          className="rounded-xl p-5"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-3">👩 שכבת האם</h3>
          <ScoreBar score={analysis.mother_analogy_score} color="#ec4899" />
          <p className="mt-3 text-sm" style={{ color: "var(--muted-foreground)" }}>
            {analysis.mother_analogy_text || "טיפוח, ויסות רגשי, קשר ודאגה"}
          </p>
        </div>
        <div
          className="rounded-xl p-5"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-3">👨 שכבת האב</h3>
          <ScoreBar score={analysis.father_analogy_score} color="#3b82f6" />
          <p className="mt-3 text-sm" style={{ color: "var(--muted-foreground)" }}>
            {analysis.father_analogy_text || "הגנה, גבולות, אסטרטגיה וסמכות"}
          </p>
        </div>
      </div>

      {analysis.son_perspective && (
        <div
          className="rounded-xl p-5"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-4">👦 נקודת המבט של הבן</h3>
          <div className="space-y-3">
            <PerspectiveRow
              label="מה קורה?"
              value={analysis.son_perspective.what_is_happening}
            />
            <PerspectiveRow
              label="מה ניתן לתפוס?"
              value={analysis.son_perspective.what_can_be_perceived}
            />
            <PerspectiveRow
              label="משמעות התפתחותית"
              value={analysis.son_perspective.developmental_meaning}
            />
            <PerspectiveRow
              label="דפוס ארוך טווח אפשרי"
              value={analysis.son_perspective.possible_long_term_pattern}
            />
            <div className="flex items-center gap-2 pt-2">
              <span className="text-sm font-medium">רמת ודאות:</span>
              <ScoreBar score={analysis.son_perspective.certainty} color="#22c55e" />
            </div>
          </div>
        </div>
      )}

      {analysis.scientific_context && (
        <div
          className="rounded-xl p-5"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-3">🔬 הקשר מדעי</h3>
          <div className="flex items-center gap-2 mb-3">
            <span
              className="px-3 py-1 rounded-full text-sm font-medium"
              style={{ background: "var(--accent)", color: "var(--accent-foreground)" }}
            >
              {EVIDENCE_LABELS[analysis.scientific_context.evidence_level] ||
                analysis.scientific_context.evidence_level}
            </span>
          </div>
          <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
            {analysis.scientific_context.text}
          </p>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        <ScoreCard
          label="ציון שלב"
          value={analysis.stage_score}
          max={100}
        />
        <ScoreCard
          label="ציון קשר לישראל"
          value={analysis.israel_relevance_score}
          max={100}
        />
        <ScoreCard
          label="ציון סופי"
          value={analysis.final_score}
          max={100}
        />
      </div>

      <div
        className="rounded-xl p-4"
        style={{ background: "var(--muted)", border: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium">סוג הטענה:</span>
          <span
            className="px-2 py-0.5 rounded-full"
            style={{ background: "var(--accent)", color: "var(--accent-foreground)" }}
          >
            {CLAIM_LABELS[analysis.claim_type] || analysis.claim_type}
          </span>
        </div>
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
  );
}

function InfoCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: string;
}) {
  return (
    <div
      className="rounded-xl p-4 text-center"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <div className="text-2xl mb-1">{icon}</div>
      <div className="font-bold text-lg">{value}</div>
      <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>
        {label}
      </div>
    </div>
  );
}

function ScoreBar({ score, color }: { score: number; color: string }) {
  return (
    <div className="flex items-center gap-3">
      <div
        className="flex-1 h-3 rounded-full overflow-hidden"
        style={{ background: "var(--muted)" }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${score}%`, background: color }}
        />
      </div>
      <span className="text-sm font-bold w-12 text-left">{score}/100</span>
    </div>
  );
}

function PerspectiveRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-sm font-medium mb-0.5">{label}</div>
      <div className="text-sm" style={{ color: "var(--muted-foreground)" }}>
        {value}
      </div>
    </div>
  );
}

function ScoreCard({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const pct = Math.round((value / max) * 100);
  return (
    <div
      className="rounded-xl p-4 text-center"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <div className="text-2xl font-bold">{value}</div>
      <div
        className="w-full h-2 rounded-full mt-2 overflow-hidden"
        style={{ background: "var(--muted)" }}
      >
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, background: "var(--primary)" }}
        />
      </div>
      <div className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
        {label}
      </div>
    </div>
  );
}
