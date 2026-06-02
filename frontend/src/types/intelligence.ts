export type IntelligenceIcon = 'spark' | 'trend' | 'alert'

export type PriorityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface IntelligenceItem {
  artifact_id: number
  title: string
  url: string
  published_at: string
  summary: string
  why_it_matters: string
  domain: string
  signal_type: string
  confidence_score: number
  validation_status: string
  strategic_score: number
  priority_level: PriorityLevel
}

export interface IntelligenceState {
  loading: boolean
  error: string | null
  data: IntelligenceItem[]
}
