export interface IntelligenceRunSummary {
  run_id: string
  started_at: string
  completed_at: string | null
  sources_polled: number
  articles_found: number
  articles_inserted: number
  articles_filtered: number
  articles_enriched: number
  articles_scored: number
  status: string
}

export interface SystemStatusResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  last_run: string | null
  next_run: string | null
  active_sources: number
  articles_today: number
  last_run_summary: IntelligenceRunSummary | null
}
