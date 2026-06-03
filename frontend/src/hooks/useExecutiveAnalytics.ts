import { useCallback, useEffect, useState } from 'react'
import {
  getAnalyticsDepartments,
  getAnalyticsFeedback,
  getAnalyticsOpportunities,
  getAnalyticsOverview,
  getAnalyticsSources,
} from '../services/api'
import type { ExecutiveAnalyticsBundle } from '../types/analytics'

export function useExecutiveAnalytics() {
  const [data, setData] = useState<ExecutiveAnalyticsBundle | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const [overview, departments, opportunities, sources, feedback] = await Promise.all([
        getAnalyticsOverview(),
        getAnalyticsDepartments(),
        getAnalyticsOpportunities(),
        getAnalyticsSources(),
        getAnalyticsFeedback(),
      ])
      setData({ overview, departments, opportunities, sources, feedback })
      setError(null)
    } catch {
      setError('Unable to load executive analytics')
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, loading, error, refresh }
}
