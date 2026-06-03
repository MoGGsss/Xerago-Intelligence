export interface RankedMetricItem {
  label: string
  count: number
  avg_score: number | null
}

export interface AnalyticsOverview {
  articles_today: number
  active_sources: number
  enriched_articles: number
  average_strategic_score: number | null
  feedback_total: number
  feedback_positive: number
  feedback_negative: number
  last_refresh_at: string | null
  last_refresh_status: string | null
}

export interface DepartmentEngagementItem {
  department_name: string
  mapped_articles: number
  feedback_count: number
  positive_count: number
  negative_count: number
}

export interface AnalyticsDepartments {
  top_departments: RankedMetricItem[]
  department_engagement: DepartmentEngagementItem[]
}

export interface AnalyticsOpportunities {
  top_opportunity_categories: RankedMetricItem[]
  top_opportunity_types: RankedMetricItem[]
}

export interface SourceContributionItem {
  source_id: string
  source_name: string
  source_tier: number | null
  active_flag: boolean | null
  article_count: number
  enriched_count: number
  avg_strategic_score: number | null
}

export interface AnalyticsSources {
  source_contribution: SourceContributionItem[]
}

export interface FeedbackTrendPoint {
  date: string
  positive: number
  negative: number
  total: number
}

export interface FeedbackSummary {
  total: number
  positive: number
  negative: number
  positive_pct: number
  trends: FeedbackTrendPoint[]
}

export interface UsefulArticleItem {
  artifact_id: string
  title: string
  url: string
  positive_count: number
  strategic_score: number | null
}

export interface AnalyticsFeedback {
  positive_vs_negative: FeedbackSummary
  most_useful_articles: UsefulArticleItem[]
}

export interface ExecutiveAnalyticsBundle {
  overview: AnalyticsOverview
  departments: AnalyticsDepartments
  opportunities: AnalyticsOpportunities
  sources: AnalyticsSources
  feedback: AnalyticsFeedback
}
