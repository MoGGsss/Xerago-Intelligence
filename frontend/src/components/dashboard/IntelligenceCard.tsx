import { useState } from 'react'
import { ChevronDown, ExternalLink } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { DepartmentImpactView, PriorityLevel } from '../../types/intelligence'
import ArticleFeedbackFooter from './ArticleFeedbackFooter'
import DepartmentImpactSection from './DepartmentImpactSection'

interface IntelligenceCardProps {
  artifactId?: string
  feedbackDepartmentName?: string | null
  priorityLevel?: PriorityLevel | string
  strategicScore?: number
  title: string
  description: string
  whyItMatters: string
  publishedAt: string
  domain: string
  url: string
  icon: LucideIcon
  departmentImpact?: DepartmentImpactView | null
  departmentLabel?: string
  onSelect?: () => void
}

function formatPublishedDate(value: string): string {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(parsed)
}

function priorityStyles(level?: string): string {
  switch (level?.toUpperCase()) {
    case 'CRITICAL':
      return 'border-rose-200 bg-rose-50 text-rose-700'
    case 'HIGH':
      return 'border-amber-200 bg-amber-50 text-amber-800'
    case 'MEDIUM':
      return 'border-sky-200 bg-sky-50 text-sky-800'
    case 'LOW':
      return 'border-slate-200 bg-slate-50 text-slate-600'
    default:
      return 'border-slate-200 bg-slate-50 text-slate-600'
  }
}

export default function IntelligenceCard({
  artifactId,
  feedbackDepartmentName,
  priorityLevel,
  strategicScore,
  title,
  description,
  whyItMatters,
  publishedAt,
  domain,
  url,
  icon: Icon,
  departmentImpact,
  departmentLabel = 'Your department',
  onSelect,
}: IntelligenceCardProps) {
  const [whyExpanded, setWhyExpanded] = useState(false)
  const formattedDate = formatPublishedDate(publishedAt)
  const scoreDisplay =
    typeof strategicScore === 'number' ? strategicScore : '—'

  return (
    <article
      className="group flex h-full flex-col overflow-visible rounded-2xl border border-slate-200/90 bg-white shadow-sm transition-all duration-300 ease-out hover:-translate-y-0.5 hover:border-emerald-200/80 hover:shadow-[0_12px_32px_rgba(15,23,42,0.1)]"
      onClick={(event) => {
        if (!onSelect) {
          return
        }
        const target = event.target as HTMLElement
        if (target.closest('a,button')) {
          return
        }
        onSelect()
      }}
      onKeyDown={(event) => {
        if (!onSelect) {
          return
        }
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onSelect()
        }
      }}
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
      aria-label={onSelect ? `Open details for ${title}` : undefined}
    >
      <div className="flex h-full flex-col p-6">
        <div className="flex items-start justify-between gap-3">
          <span
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 text-emerald-600 ring-1 ring-emerald-100/80"
            aria-hidden="true"
          >
            <Icon size={18} strokeWidth={2} />
          </span>
          <div className="flex flex-wrap items-center justify-end gap-2">
            {priorityLevel ? (
              <span
                className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${priorityStyles(priorityLevel)}`}
              >
                {priorityLevel}
              </span>
            ) : null}
            <span className="inline-flex items-center rounded-lg bg-slate-900 px-2.5 py-1 text-xs font-semibold tabular-nums text-white">
              {scoreDisplay}
            </span>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="inline-flex max-w-full items-center truncate rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
            {domain}
          </span>
          <time
            dateTime={publishedAt}
            className="text-xs font-medium text-slate-400"
          >
            {formattedDate}
          </time>
        </div>

        <h3 className="mt-4 line-clamp-2 text-lg font-semibold leading-snug tracking-tight text-slate-900">
          {title}
        </h3>

        <p className="mt-3 line-clamp-4 text-sm leading-relaxed text-slate-600">
          {description}
        </p>

        {departmentImpact ? (
          <DepartmentImpactSection
            impact={departmentImpact}
            departmentLabel={departmentLabel}
          />
        ) : null}

        <div className="mt-4 flex-1 border-t border-slate-100 pt-4">
          <button
            type="button"
            onClick={() => setWhyExpanded((open) => !open)}
            aria-expanded={whyExpanded}
            className="flex w-full items-center justify-between gap-2 rounded-lg px-1 py-1 text-left text-sm font-semibold text-slate-700 transition-colors duration-200 hover:text-emerald-700"
          >
            <span>Why It Matters</span>
            <ChevronDown
              size={16}
              className={`shrink-0 text-slate-400 transition-transform duration-200 ${whyExpanded ? 'rotate-180' : ''}`}
              aria-hidden="true"
            />
          </button>
          <div
            className={`grid transition-all duration-300 ease-out ${whyExpanded ? 'mt-2 grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
          >
            <div className="overflow-hidden">
              <p className="rounded-lg bg-slate-50 px-3 py-2.5 text-sm leading-relaxed text-slate-600">
                {whyItMatters}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2 border-t border-slate-100 pt-4">
          <a
            href={url}
            target="_blank"
            rel="noreferrer noopener"
            className="inline-flex h-8 shrink-0 items-center gap-1 rounded-lg bg-emerald-600 px-3 text-sm font-semibold text-white no-underline shadow-sm transition-all duration-200 hover:bg-emerald-700 hover:shadow-md"
          >
            Read Article
            <ExternalLink size={13} strokeWidth={2.5} aria-hidden="true" />
          </a>
          {artifactId && feedbackDepartmentName ? (
            <ArticleFeedbackFooter
              artifactId={artifactId}
              departmentName={feedbackDepartmentName}
            />
          ) : null}
        </div>
      </div>
    </article>
  )
}
