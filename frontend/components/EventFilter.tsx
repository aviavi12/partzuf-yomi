"use client";

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

interface Props {
  eventTypes: string[];
  selected: string | null;
  onSelect: (type: string | null) => void;
}

export default function EventFilter({ eventTypes, selected, onSelect }: Props) {
  if (eventTypes.length === 0) return null;

  return (
    <div className="flex gap-1.5 flex-wrap">
      <button
        onClick={() => onSelect(null)}
        className="px-2.5 py-1 rounded-lg text-xs transition-colors"
        style={{
          background: selected === null ? "var(--primary)" : "var(--muted)",
          color: selected === null ? "var(--primary-foreground)" : "var(--muted-foreground)",
        }}
      >
        כל הסוגים
      </button>
      {eventTypes.map((et) => (
        <button
          key={et}
          onClick={() => onSelect(selected === et ? null : et)}
          className="px-2.5 py-1 rounded-lg text-xs transition-colors"
          style={{
            background: selected === et ? "var(--primary)" : "var(--muted)",
            color: selected === et ? "var(--primary-foreground)" : "var(--muted-foreground)",
          }}
        >
          {EVENT_LABELS[et] || et}
        </button>
      ))}
    </div>
  );
}
