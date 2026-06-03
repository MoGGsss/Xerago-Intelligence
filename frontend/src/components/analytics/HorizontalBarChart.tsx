import type { RankedMetricItem } from '../../types/analytics'

interface HorizontalBarChartProps {
  title: string
  subtitle?: string
  items: RankedMetricItem[]
  valueKey?: 'count' | 'avg_score'
  emptyMessage?: string
}

export default function HorizontalBarChart({
  title,
  subtitle,
  items,
  valueKey = 'avg_score',
  emptyMessage = 'No data yet',
}: HorizontalBarChartProps) {
  const values = items.map((item) =>
    valueKey === 'avg_score' ? (item.avg_score ?? 0) : item.count,
  )
  const maxValue = Math.max(...values, 1)

  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
      <header className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-slate-500">{subtitle}</p> : null}
      </header>
      {items.length === 0 ? (
        <p className="text-sm text-slate-400">{emptyMessage}</p>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => {
            const value = valueKey === 'avg_score' ? (item.avg_score ?? 0) : item.count
            const widthPct = Math.max(4, Math.round((value / maxValue) * 100))
            return (
              <li key={item.label}>
                <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                  <span className="truncate font-medium text-slate-700">{item.label}</span>
                  <span className="shrink-0 tabular-nums text-slate-500">
                    {valueKey === 'avg_score' ? `${value}` : value}
                    {valueKey === 'avg_score' ? '' : ` · avg ${item.avg_score ?? '—'}`}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all"
                    style={{ width: `${widthPct}%` }}
                  />
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </article>
  )
}
