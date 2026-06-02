import type { IntelligenceItem, PriorityLevel } from '../types/intelligence'

export interface IntelligenceHeaderStats {
  totalCount: number
  criticalCount: number
  highPriorityCount: number
  averageStrategicScore: number
  lastUpdated: string | null
  newTodayCount: number
  newThisWeekCount: number
  criticalChange: number
}

function normalizePriority(level: string | undefined): PriorityLevel | null {
  if (!level) {
    return null
  }
  const upper = level.toUpperCase()
  if (
    upper === 'LOW' ||
    upper === 'MEDIUM' ||
    upper === 'HIGH' ||
    upper === 'CRITICAL'
  ) {
    return upper
  }
  return null
}

function formatLastUpdated(value: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(value)
}

/** Derive dashboard header metrics from loaded intelligence records. */
export function computeIntelligenceHeaderStats(
  items: IntelligenceItem[],
): IntelligenceHeaderStats {
  let latestPublishedMs = Number.NEGATIVE_INFINITY

  let criticalCount = 0
  let highPriorityCount = 0
  let totalStrategicScore = 0
  let strategicScoreCount = 0
  let newTodayCount = 0
  let newThisWeekCount = 0
  let criticalThisWeek = 0
  let criticalPreviousWeek = 0
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const weekStart = new Date(todayStart)
  weekStart.setDate(weekStart.getDate() - 7)
  const previousWeekStart = new Date(todayStart)
  previousWeekStart.setDate(previousWeekStart.getDate() - 14)

  for (const item of items) {
    const priority = normalizePriority(item.priority_level)
    if (priority === 'CRITICAL') {
      criticalCount += 1
    }
    if (priority === 'HIGH') {
      highPriorityCount += 1
    }
    if (typeof item.strategic_score === 'number') {
      totalStrategicScore += item.strategic_score
      strategicScoreCount += 1
    }

    const publishedMs = new Date(item.published_at).getTime()
    if (!Number.isNaN(publishedMs) && publishedMs > latestPublishedMs) {
      latestPublishedMs = publishedMs
    }
    if (!Number.isNaN(publishedMs)) {
      const publishedDate = new Date(publishedMs)
      if (publishedDate >= todayStart) {
        newTodayCount += 1
      }
      if (publishedDate >= weekStart) {
        newThisWeekCount += 1
      }
      if (priority === 'CRITICAL') {
        if (publishedDate >= weekStart) {
          criticalThisWeek += 1
        } else if (publishedDate >= previousWeekStart && publishedDate < weekStart) {
          criticalPreviousWeek += 1
        }
      }
    }
  }

  return {
    totalCount: items.length,
    criticalCount,
    highPriorityCount,
    averageStrategicScore:
      strategicScoreCount > 0
        ? Math.round((totalStrategicScore / strategicScoreCount) * 10) / 10
        : 0,
    newTodayCount,
    newThisWeekCount,
    criticalChange: criticalThisWeek - criticalPreviousWeek,
    lastUpdated:
      latestPublishedMs > Number.NEGATIVE_INFINITY
        ? formatLastUpdated(new Date(latestPublishedMs))
        : null,
  }
}
