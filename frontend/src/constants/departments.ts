/** Canonical Xerago company departments (mirrors backend taxonomy, Phase 1A). */

export interface CompanyDepartment {
  slug: string
  label: string
}

export const COMPANY_DEPARTMENTS: readonly CompanyDepartment[] = [
  { slug: 'ai-engineering', label: 'AI Engineering' },
  { slug: 'solutions', label: 'Solutions' },
  { slug: 'digital-analytics', label: 'Digital Analytics' },
  { slug: 'strategy-design-innovation', label: 'Strategy, Design & Innovation' },
  { slug: 'digital-operations', label: 'Digital Operations' },
  { slug: 'sales', label: 'Sales' },
  { slug: 'account-management', label: 'Account Management' },
  { slug: 'content-digital-marketing', label: 'Content & Digital Marketing' },
  { slug: 'martech-campaign-services', label: 'MarTech & Campaign Services' },
  { slug: 'xerago-securities', label: 'Xerago Securities' },
] as const

/** Legacy slug -> canonical slug (login URLs and bookmarks). */
export const DEPARTMENT_SLUG_ALIASES: Readonly<Record<string, string>> = {
  administration: 'strategy-design-innovation',
  'campaign-services': 'martech-campaign-services',
  content: 'content-digital-marketing',
  'digital-marketing': 'content-digital-marketing',
  'finance-legal': 'account-management',
  'founders-office': 'strategy-design-innovation',
  hr: 'strategy-design-innovation',
  'it-operations-support': 'digital-operations',
  martech: 'martech-campaign-services',
  'new-initiatives': 'strategy-design-innovation',
  operations: 'digital-operations',
  'partner-management': 'sales',
  'program-management': 'solutions',
  qc: 'digital-operations',
  'revenue-growth': 'sales',
  'strategy-design': 'strategy-design-innovation',
}

/** Legacy display label -> canonical label. */
export const DEPARTMENT_LABEL_ALIASES: Readonly<Record<string, string>> = {
  Administration: 'Strategy, Design & Innovation',
  'Campaign Services': 'MarTech & Campaign Services',
  Content: 'Content & Digital Marketing',
  'Digital Marketing': 'Content & Digital Marketing',
  'Finance & Legal': 'Account Management',
  "Founder's Office": 'Strategy, Design & Innovation',
  HR: 'Strategy, Design & Innovation',
  'IT Operations & Support': 'Digital Operations',
  MarTech: 'MarTech & Campaign Services',
  'New Initiatives': 'Strategy, Design & Innovation',
  Operations: 'Digital Operations',
  'Partner Management': 'Sales',
  'Program Management': 'Solutions',
  QC: 'Digital Operations',
  'Revenue Growth': 'Sales',
  'Strategy & Design': 'Strategy, Design & Innovation',
}

/** Primary dashboard sections (most actionable for demo). */
export const FEATURED_DEPARTMENT_SLUGS: readonly string[] = [
  'ai-engineering',
  'martech-campaign-services',
  'digital-analytics',
  'solutions',
  'strategy-design-innovation',
] as const

export const DEPARTMENT_BY_SLUG = Object.fromEntries(
  COMPANY_DEPARTMENTS.map((dept) => [dept.slug, dept]),
) as Record<string, CompanyDepartment>

export const DEPARTMENT_BY_LABEL = Object.fromEntries(
  COMPANY_DEPARTMENTS.map((dept) => [dept.label, dept]),
) as Record<string, CompanyDepartment>

export function resolveDepartmentSlug(slug: string): string {
  const normalized = slug.trim().toLowerCase()
  return DEPARTMENT_SLUG_ALIASES[normalized] ?? normalized
}

export function resolveDepartmentLabel(label: string): string {
  const trimmed = label.trim()
  return DEPARTMENT_LABEL_ALIASES[trimmed] ?? trimmed
}

export function departmentLabelForSlug(slug: string): string {
  const canonical = resolveDepartmentSlug(slug)
  return DEPARTMENT_BY_SLUG[canonical]?.label ?? slug
}

export function departmentForSlug(slug: string): CompanyDepartment | undefined {
  const canonical = resolveDepartmentSlug(slug)
  return DEPARTMENT_BY_SLUG[canonical]
}
