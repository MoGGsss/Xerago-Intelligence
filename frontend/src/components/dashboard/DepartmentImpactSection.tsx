import type { ReactNode } from 'react'
import type { DepartmentImpactView } from '../../types/intelligence'

interface DepartmentImpactSectionProps {
  impact: DepartmentImpactView
  departmentLabel: string
}

function ImpactRow({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:gap-3">
      <dt className="shrink-0 text-[11px] font-semibold uppercase tracking-wide text-slate-500 sm:w-28 sm:pt-0.5">
        {label}
      </dt>
      <dd className="min-w-0 flex-1 text-sm leading-relaxed text-slate-700">{children}</dd>
    </div>
  )
}

export default function DepartmentImpactSection({
  impact,
  departmentLabel,
}: DepartmentImpactSectionProps) {
  const scoreDisplay =
    typeof impact.department_opportunity_score === 'number'
      ? impact.department_opportunity_score
      : null

  return (
    <section
      className="mt-4 rounded-xl border border-emerald-100/90 bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/40 p-4 ring-1 ring-emerald-100/60"
      aria-labelledby={`department-impact-${departmentLabel.replace(/\s+/g, '-')}`}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h4
          id={`department-impact-${departmentLabel.replace(/\s+/g, '-')}`}
          className="text-xs font-bold uppercase tracking-[0.14em] text-emerald-800"
        >
          Department Impact
        </h4>
        <div className="flex flex-wrap items-center gap-2">
          {impact.impact_category ? (
            <span className="inline-flex max-w-full items-center rounded-full border border-emerald-200 bg-emerald-100/90 px-2.5 py-1 text-[11px] font-semibold text-emerald-900">
              {impact.impact_category}
            </span>
          ) : null}
          {impact.opportunity_type ? (
            <span className="inline-flex max-w-full items-center rounded-full border border-teal-200 bg-teal-50 px-2.5 py-1 text-[11px] font-semibold text-teal-900">
              {impact.opportunity_type}
            </span>
          ) : null}
          {scoreDisplay !== null ? (
            <span
              className="inline-flex items-center rounded-lg bg-slate-900 px-2.5 py-1 text-xs font-bold tabular-nums text-white"
              title="Department opportunity score"
            >
              {scoreDisplay}
            </span>
          ) : null}
        </div>
      </div>

      <dl className="space-y-2.5">
        {impact.impact_summary ? (
          <ImpactRow label="Impact">
            <p className="font-medium text-slate-800">{impact.impact_summary}</p>
          </ImpactRow>
        ) : null}
        {impact.impact_category ? (
          <ImpactRow label="Category">
            <span className="inline-flex rounded-md border border-emerald-200/80 bg-white px-2 py-0.5 text-sm font-medium text-emerald-800">
              {impact.impact_category}
            </span>
          </ImpactRow>
        ) : null}
        {impact.opportunity_type ? (
          <ImpactRow label="Opportunity">
            <span className="inline-flex rounded-md border border-teal-200/80 bg-white px-2 py-0.5 text-sm font-medium text-teal-900">
              {impact.opportunity_type}
            </span>
          </ImpactRow>
        ) : null}
        {scoreDisplay !== null ? (
          <ImpactRow label="Opportunity Score">
            <span className="inline-flex w-fit items-center rounded-lg bg-emerald-700 px-3 py-1 text-sm font-bold tabular-nums text-white shadow-sm">
              {scoreDisplay}
            </span>
          </ImpactRow>
        ) : null}
      </dl>
    </section>
  )
}
