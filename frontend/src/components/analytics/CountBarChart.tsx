import type { RankedMetricItem } from '../../types/analytics'

interface CountBarChartProps {
  title: string
  subtitle?: string
  items: RankedMetricItem[]
  barClassName?: string
}

export default function CountBarChart({
  title,
  subtitle,
  items,
  barClassName = 'bg-emerald-500',
}: CountBarChartProps) {
  const maxCount = Math.max(...items.map((item) => item.count), 1)

  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
      <header className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-slate-500">{subtitle}</p> : null}
      </header>
      {items.length === 0 ? (
        <p className="text-sm text-slate-400">No data yet</p>
      ) : (
        <div className="flex h-52 items-end gap-2">
          {items.map((item) => {
            const heightPct = Math.max(8, Math.round((item.count / maxCount) * 100))
            return (
              <div
                key={item.label}
                className="flex min-w-0 flex-1 flex-col items-center justify-end gap-2"
              >
                <span className="text-[10px] font-semibold tabular-nums text-slate-600">
                  {item.count}
                </span>
                <div
                  className={`w-full rounded-t-md ${barClassName}`}
                  style={{ height: `${heightPct}%` }}
                  title={`${item.label}: ${item.count}`}
                />
                <span className="line-clamp-2 w-full text-center text-[10px] leading-tight text-slate-500">
                  {item.label}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </article>
  )
}
