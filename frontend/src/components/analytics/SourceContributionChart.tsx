import type { SourceContributionItem } from '../../types/analytics'

interface SourceContributionChartProps {
  items: SourceContributionItem[]
}

export default function SourceContributionChart({ items }: SourceContributionChartProps) {
  const maxArticles = Math.max(...items.map((item) => item.article_count), 1)

  return (
    <article className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
      <header className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Source Contribution</h3>
        <p className="mt-1 text-xs text-slate-500">Articles ingested and enriched by RSS source</p>
      </header>
      {items.length === 0 ? (
        <p className="text-sm text-slate-400">No source activity yet</p>
      ) : (
        <ul className="max-h-80 space-y-3 overflow-y-auto pr-1">
          {items.map((item) => {
            const widthPct = Math.max(4, Math.round((item.article_count / maxArticles) * 100))
            const enrichPct =
              item.article_count > 0
                ? Math.round((item.enriched_count / item.article_count) * 100)
                : 0
            return (
              <li key={item.source_id}>
                <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                  <span className="truncate font-medium text-slate-700">
                    {item.source_name}
                    {item.source_tier ? (
                      <span className="ml-1 text-slate-400">T{item.source_tier}</span>
                    ) : null}
                  </span>
                  <span className="shrink-0 tabular-nums text-slate-500">
                    {item.article_count} articles · {enrichPct}% enriched
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-500"
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
