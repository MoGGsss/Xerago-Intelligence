import axios from 'axios'
import type { FeedbackCreatePayload, FeedbackCreateResponse } from '../types/feedback'
import type { IntelligenceItem } from '../types/intelligence'
import type {
  AnalyticsDepartments,
  AnalyticsFeedback,
  AnalyticsOpportunities,
  AnalyticsOverview,
  AnalyticsSources,
} from '../types/analytics'
import type {
  PrototypeArticleListResponse,
  PrototypeDatasetSummary,
} from '../types/prototype'
import type { SystemStatusResponse } from '../types/system'

const API_BASE_URL = import.meta.env.DEV ? '' : 'http://127.0.0.1:8000'

export interface IntelligenceListResponse {
  items: IntelligenceItem[]
  page: number
  page_size: number
  total: number
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getIntelligenceList(
  params: {
    page?: number
    page_size?: number
    department?: string
    domain?: string
    priority?: string
    q?: string
  } = {},
): Promise<IntelligenceListResponse> {
  const response = await apiClient.get<IntelligenceListResponse>('/v1/intelligence', {
    params,
  })
  return response.data
}

export async function getTopIntelligence(limit = 100): Promise<IntelligenceItem[]> {
  if (limit > 50) {
    const result = await getIntelligenceList({ page: 1, page_size: limit })
    return result.items
  }

  const response = await apiClient.get<IntelligenceItem[] | { data: IntelligenceItem[] }>(
    '/v1/intelligence/top',
    { params: { limit } },
  )

  if (Array.isArray(response.data)) {
    return response.data
  }

  return response.data.data ?? []
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  const response = await apiClient.get<SystemStatusResponse>('/v1/system/status')
  return response.data
}

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const response = await apiClient.get<AnalyticsOverview>('/v1/analytics/overview')
  return response.data
}

export async function getAnalyticsDepartments(): Promise<AnalyticsDepartments> {
  const response = await apiClient.get<AnalyticsDepartments>('/v1/analytics/departments')
  return response.data
}

export async function getAnalyticsOpportunities(): Promise<AnalyticsOpportunities> {
  const response = await apiClient.get<AnalyticsOpportunities>('/v1/analytics/opportunities')
  return response.data
}

export async function getAnalyticsSources(): Promise<AnalyticsSources> {
  const response = await apiClient.get<AnalyticsSources>('/v1/analytics/sources')
  return response.data
}

export async function getAnalyticsFeedback(): Promise<AnalyticsFeedback> {
  const response = await apiClient.get<AnalyticsFeedback>('/v1/analytics/feedback')
  return response.data
}

export async function submitArticleFeedback(
  payload: FeedbackCreatePayload,
): Promise<FeedbackCreateResponse> {
  const body =
    payload.feedback_type === 'positive'
      ? {
          artifact_id: payload.artifact_id,
          department_name: payload.department_name,
          feedback_type: payload.feedback_type,
        }
      : payload

  const response = await apiClient.post<FeedbackCreateResponse>('/v1/feedback', body)
  return response.data
}

export async function getPrototypeSummary(): Promise<PrototypeDatasetSummary> {
  const response = await apiClient.get<PrototypeDatasetSummary>('/v1/prototype/summary')
  return response.data
}

export async function getPrototypeArticles(
  departmentSlug?: string,
): Promise<PrototypeArticleListResponse> {
  const response = await apiClient.get<PrototypeArticleListResponse>('/v1/prototype/articles', {
    params: departmentSlug ? { department_slug: departmentSlug } : undefined,
  })
  return response.data
}

export { API_BASE_URL }
