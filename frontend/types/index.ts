export interface NewsArticle {
  id: string;
  source_id: string;
  source_name: string | null;
  external_id: string | null;
  headline: string;
  summary: string | null;
  content: string | null;
  url: string | null;
  language: string;
  published_at: string | null;
  collected_at: string;
  content_hash: string;
  is_demo: boolean;
  is_analyzed: boolean;
  cluster_id: string | null;
  created_at: string;
}

export interface NewsListResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  page_size: number;
}

export interface SonPerspective {
  what_is_happening: string;
  what_can_be_perceived: string;
  developmental_meaning: string;
  possible_long_term_pattern: string;
  certainty: number;
}

export interface ScientificContext {
  evidence_level: string;
  text: string;
}

export interface FullAnalysis {
  article_id: string;
  headline: string;
  source_name: string | null;
  url: string | null;
  published_at: string | null;
  event_type: string | null;
  event_type_label_he: string | null;
  developmental_stage: string | null;
  stage_label_he: string | null;
  stage_score: number;
  israel_relevance_type: string | null;
  israel_relevance_score: number;
  mother_analogy_score: number;
  mother_analogy_text: string | null;
  father_analogy_score: number;
  father_analogy_text: string | null;
  son_perspective: SonPerspective | null;
  scientific_context: ScientificContext | null;
  confidence: number;
  final_score: number;
  claim_type: string;
}

export interface DashboardStats {
  total_articles_today: number;
  global_articles_today: number;
  israel_articles_today: number;
  avg_israel_relevance: number;
  dominant_stage: string | null;
  dominant_stage_label_he: string | null;
  avg_confidence: number;
  stage_distribution: Record<string, number>;
  event_type_distribution: Record<string, number>;
  israel_relevance_distribution: Record<string, number>;
}

export interface StageInfo {
  value: string;
  label_he: string;
  order: number;
}

export interface EventTypeInfo {
  value: string;
  label_he: string;
}

export interface DailySummaryResponse {
  id: string;
  summary_date: string;
  total_articles: number;
  global_articles: number;
  israel_articles: number;
  dominant_stage: string | null;
  secondary_stage: string | null;
  trend_text: string | null;
  confidence: number;
  telegram_sent: boolean;
  created_at: string;
}
