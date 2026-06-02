import type { IntelligenceHeaderStats } from '../../utils/intelligenceStats'

interface DashboardMetricsProps {
  stats: IntelligenceHeaderStats
  loading?: boolean
}

function MetricCard({
  label,
  value,
  accentClass,
  trend,
}: {
  label: string
  value: string | number
  accentClass?: string
  trend?: string
}) {
  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-4 shadow-sm transition-all duration-200 hover:border-slate-300 hover:shadow-md md:p-5">
      <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
        {label}
      </p>
      <p
        className={`mt-2 text-3xl font-semibold tabular-nums tracking-tight text-slate-900 ${accentClass ?? ''}`}
      >
        {value}
      </p>
      {trend ? (
        <p className="mt-1 text-xs font-semibold text-emerald-600">{trend}</p>
      ) : null}
    </article>
  )
}

function MetricsSkeleton() {
  return (
    <section className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <div
          key={index}
          className="h-[98px] animate-pulse rounded-2xl border border-slate-200 bg-slate-100"
        />
      ))}
    </section>
  )
}

export default function DashboardMetrics({
  stats,
  loading = false,
}: DashboardMetricsProps) {
  if (loading) {
    return <MetricsSkeleton />
  }

  return (
    <section className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Total Signals" value={stats.totalCount} />
      <MetricCard
        label="Critical Signals"
        value={stats.criticalCount}
        accentClass={stats.criticalCount > 0 ? 'text-rose-600' : undefined}
        trend={`↑ New Today ${stats.newTodayCount}`}
      />
      <MetricCard
        label="High Signals"
        value={stats.highPriorityCount}
        accentClass={stats.highPriorityCount > 0 ? 'text-amber-600' : undefined}
        trend={`↑ New This Week ${stats.newThisWeekCount}`}
      />
      <MetricCard
        label="Average Strategic Score"
        value={stats.averageStrategicScore.toFixed(1)}
        trend={`Critical Change ${
          stats.criticalChange >= 0 ? `+${stats.criticalChange}` : stats.criticalChange
        }`}
      />
    </section>
  )
}
