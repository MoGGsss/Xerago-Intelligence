import type { FeedbackSummary } from '../../types/analytics'

interface FeedbackTrendChartProps {
  summary: FeedbackSummary
}

export default function FeedbackTrendChart({ summary }: FeedbackTrendChartProps) {
  const maxTotal = Math.max(...summary.trends.map((point) => point.total), 1)

  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
      <header className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Feedback Trends</h3>
          <p className="mt-1 text-xs text-slate-500">Positive vs negative over recent days</p>
        </div>
        <div className="flex gap-4 text-xs">
          <span className="font-semibold text-emerald-600">
            Positive {summary.positive} ({summary.positive_pct}%)
          </span>
          <span className="font-semibold text-rose-600">Negative {summary.negative}</span>
        </div>
      </header>

      {summary.trends.length === 0 ? (
        <p className="text-sm text-slate-400">No feedback recorded yet</p>
      ) : (
        <>
          <div className="flex h-48 items-end gap-1.5">
            {summary.trends.map((point) => {
              const positiveHeight = Math.max(
                2,
                Math.round((point.positive / maxTotal) * 100),
              )
              const negativeHeight = Math.max(
                2,
                Math.round((point.negative / maxTotal) * 100),
              )
              const label = new Date(point.date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })
              return (
                <div
                  key={point.date}
                  className="flex min-w-0 flex-1 flex-col items-center justify-end gap-1"
                >
                  <div className="flex w-full items-end justify-center gap-0.5" style={{ height: '100%' }}>
                    <div
                      className="w-[42%] rounded-t bg-emerald-500"
                      style={{ height: `${positiveHeight}%` }}
                      title={`${label}: ${point.positive} positive`}
                    />
                    <div
                      className="w-[42%] rounded-t bg-rose-400"
                      style={{ height: `${negativeHeight}%` }}
                      title={`${label}: ${point.negative} negative`}
                    />
                  </div>
                  <span className="text-[9px] text-slate-500">{label}</span>
                </div>
              )
            })}
          </div>
          <div className="mt-3 flex gap-4 text-[11px] text-slate-500">
            <span className="inline-flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-emerald-500" />
              Positive
            </span>
            <span className="inline-flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-rose-400" />
              Negative
            </span>
          </div>
        </>
      )}
    </article>
  )
}
