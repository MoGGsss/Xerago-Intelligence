import { useEffect, useState } from 'react'
import { getTopIntelligence } from '../services/api'
import type { IntelligenceState } from '../types/intelligence'

export function useIntelligence(): IntelligenceState {
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<IntelligenceState['data']>([])

  useEffect(() => {
    let isMounted = true

    const fetchTopIntelligence = async () => {
      setLoading(true)
      setError(null)

      try {
        const intelligence = await getTopIntelligence()
        if (isMounted) {
          setData(intelligence)
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

    void fetchTopIntelligence()

    return () => {
      isMounted = false
    }
  }, [])

  return { loading, error, data }
}
