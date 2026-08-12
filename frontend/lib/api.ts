import type {
  DashboardStats,
  NewsListResponse,
  FullAnalysis,
  StageInfo,
  EventTypeInfo,
  DailySummaryResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getDashboard(): Promise<DashboardStats> {
  return fetchApi<DashboardStats>("/api/dashboard");
}

export async function getNews(params?: {
  page?: number;
  source?: string;
  event_type?: string;
  stage?: string;
}): Promise<NewsListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.source) searchParams.set("source", params.source);
  if (params?.event_type) searchParams.set("event_type", params.event_type);
  if (params?.stage) searchParams.set("stage", params.stage);
  const qs = searchParams.toString();
  return fetchApi<NewsListResponse>(`/api/news${qs ? `?${qs}` : ""}`);
}

export async function getAnalysis(articleId: string): Promise<FullAnalysis> {
  return fetchApi<FullAnalysis>(`/api/analysis/${articleId}`);
}

export async function getStages(): Promise<StageInfo[]> {
  return fetchApi<StageInfo[]>("/api/stages");
}

export async function getEventTypes(): Promise<EventTypeInfo[]> {
  return fetchApi<EventTypeInfo[]>("/api/event-types");
}

export async function getDailySummary(
  date?: string
): Promise<DailySummaryResponse | null> {
  const qs = date ? `?summary_date=${date}` : "";
  const res = await fetch(`${API_BASE}/api/daily-summary${qs}`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  const text = await res.text();
  if (!text || text === "null") return null;
  return JSON.parse(text);
}
