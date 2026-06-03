import { useCallback, useEffect, useState } from 'react'
import { getSystemStatus } from '../services/api'
import type { SystemStatusResponse } from '../types/system'

const POLL_INTERVAL_MS = 60_000

export function useSystemStatus() {
  const [data, setData] = useState<SystemStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const status = await getSystemStatus()
      setData(status)
      setError(null)
    } catch {
      setError('Unable to load sync status')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
    const timer = window.setInterval(() => {
      void refresh()
    }, POLL_INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [refresh])

  return { data, loading, error, refresh }
}
