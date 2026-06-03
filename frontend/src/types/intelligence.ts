export type IntelligenceIcon = 'spark' | 'trend' | 'alert'

export type PriorityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface DepartmentMappingItem {
  department_name: string
  department_relevance_score: number
  impact_summary?: string | null
  impact_category?: string | null
  opportunity_type?: string | null
  department_opportunity_score?: number | null
  impact_reason?: string | null
  impact_version?: string | null
}

/** Impact fields for the logged-in department only (dashboard cards). */
export interface DepartmentImpactView {
  impact_summary: string | null
  impact_category: string | null
  opportunity_type: string | null
  department_opportunity_score: number | null
}

export interface IntelligenceItem {
  artifact_id: string
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
  departments?: DepartmentMappingItem[]
  department?: string | null
}

export interface IntelligenceState {
  loading: boolean
  error: string | null
  data: IntelligenceItem[]
}
