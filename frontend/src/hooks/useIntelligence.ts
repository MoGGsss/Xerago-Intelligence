import { useEffect, useState } from 'react'
import { getLoggedInDepartment } from '../auth/demoAuth'
import { getIntelligenceList } from '../services/api'
import type { IntelligenceState } from '../types/intelligence'
import { sortByDepartmentRelevance } from '../utils/departmentFilters'

export function useIntelligence(): IntelligenceState {
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<IntelligenceState['data']>([])

  useEffect(() => {
    let isMounted = true
    const department = getLoggedInDepartment()

    const fetchDepartmentIntelligence = async () => {
      setLoading(true)
      setError(null)

      if (!department) {
        if (isMounted) {
          setData([])
          setError('No department selected.')
          setLoading(false)
        }
        return
      }

      try {
        const result = await getIntelligenceList({
          page: 1,
          page_size: 100,
          department,
        })
        const sorted = sortByDepartmentRelevance(result.items, department)
        if (isMounted) {
          setData(sorted)
        }
      } catch {
        if (isMounted) {
          setError('Failed to load intelligence.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    void fetchDepartmentIntelligence()

    return () => {
      isMounted = false
    }
  }, [])

  return { loading, error, data }
}
