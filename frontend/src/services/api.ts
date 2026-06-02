import axios from 'axios'
import type { IntelligenceItem } from '../types/intelligence'

const API_BASE_URL = import.meta.env.DEV ? '' : 'http://127.0.0.1:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getTopIntelligence(): Promise<IntelligenceItem[]> {
  const response = await apiClient.get<IntelligenceItem[] | { data: IntelligenceItem[] }>(
    '/v1/intelligence/top',
  )

  if (Array.isArray(response.data)) {
    return response.data
  }

  return response.data.data ?? []
}

export { API_BASE_URL }
