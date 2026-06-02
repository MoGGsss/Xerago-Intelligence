import { useMemo, useState } from 'react'
import { Copy, ExternalLink, X } from 'lucide-react'
import type { IntelligenceItem } from '../../types/intelligence'

interface IntelligenceDetailPanelProps {
  item: IntelligenceItem | null
  open: boolean
  onClose: () => void
}

function formatDateTime(value: string): string {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(parsed)
}

export default function IntelligenceDetailPanel({
  item,
  open,
  onClose,
}: IntelligenceDetailPanelProps) {
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle')

  const publishedAt = useMemo(
    () => (item ? formatDateTime(item.published_at) : ''),
    [item],
  )

  if (!open || !item) {
    return null
  }

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(item.url)
      setCopyState('copied')
    } catch {
      setCopyState('failed')
    }
    window.setTimeout(() => setCopyState('idle'), 1500)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 p-0 backdrop-blur-[1px] md:items-stretch md:justify-end"
      onClick={onClose}
      role="presentation"
    >
      <aside
        className="h-[88vh] w-full overflow-y-auto rounded-t-2xl border border-slate-200 bg-white p-6 shadow-2xl md:h-full md:w-[560px] md:rounded-none md:border-l"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Intelligence detail"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-600">
              Intelligence Detail
            </p>
            <h2 className="mt-2 text-2xl font-semibold leading-tight text-slate-900">
              {item.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close detail panel"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Domain
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-800">{item.domain}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Priority
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-800">
              {item.priority_level}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Strategic score
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-800">
              {item.strategic_score}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Confidence
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-800">
              {item.confidence_score}
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-5">
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Summary
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-700">{item.summary}</p>
          </section>

          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Why it matters
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-700">
              {item.why_it_matters}
            </p>
          </section>

          <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="grid grid-cols-1 gap-3 text-sm text-slate-700">
              <p>
                <span className="font-semibold text-slate-900">Signal type:</span>{' '}
                {item.signal_type}
              </p>
              <p>
                <span className="font-semibold text-slate-900">Published at:</span>{' '}
                {publishedAt}
              </p>
            </div>
          </section>
        </div>

        <div className="mt-7 flex flex-wrap items-center gap-3 border-t border-slate-100 pt-5">
          <a
            href={item.url}
            target="_blank"
            rel="noreferrer noopener"
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white no-underline transition-colors hover:bg-emerald-700"
          >
            Read Original Article
            <ExternalLink size={14} />
          </a>
          <button
            type="button"
            onClick={() => void copyLink()}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >
            <Copy size={14} />
            {copyState === 'copied'
              ? 'Copied'
              : copyState === 'failed'
                ? 'Copy failed'
                : 'Copy Link'}
          </button>
        </div>
      </aside>
    </div>
  )
}
