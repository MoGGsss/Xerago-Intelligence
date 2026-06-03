/** Canonical Xerago company departments (mirrors backend taxonomy). */

export interface CompanyDepartment {
  slug: string
  label: string
}

export const COMPANY_DEPARTMENTS: readonly CompanyDepartment[] = [
  { slug: 'account-management', label: 'Account Management' },
  { slug: 'administration', label: 'Administration' },
  { slug: 'ai-engineering', label: 'AI Engineering' },
  { slug: 'campaign-services', label: 'Campaign Services' },
  { slug: 'content', label: 'Content' },
  { slug: 'digital-analytics', label: 'Digital Analytics' },
  { slug: 'digital-marketing', label: 'Digital Marketing' },
  { slug: 'digital-operations', label: 'Digital Operations' },
  { slug: 'finance-legal', label: 'Finance & Legal' },
  { slug: 'founders-office', label: "Founder's Office" },
  { slug: 'hr', label: 'HR' },
  { slug: 'it-operations-support', label: 'IT Operations & Support' },
  { slug: 'martech', label: 'MarTech' },
  { slug: 'new-initiatives', label: 'New Initiatives' },
  { slug: 'operations', label: 'Operations' },
  { slug: 'partner-management', label: 'Partner Management' },
  { slug: 'program-management', label: 'Program Management' },
  { slug: 'qc', label: 'QC' },
  { slug: 'revenue-growth', label: 'Revenue Growth' },
  { slug: 'sales', label: 'Sales' },
  { slug: 'solutions', label: 'Solutions' },
  { slug: 'strategy-design', label: 'Strategy & Design' },
  { slug: 'xerago-securities', label: 'Xerago Securities' },
] as const

/** Primary dashboard sections (most actionable for demo). */
export const FEATURED_DEPARTMENT_SLUGS: readonly string[] = [
  'ai-engineering',
  'martech',
  'digital-analytics',
  'solutions',
  'founders-office',
] as const

export const DEPARTMENT_BY_SLUG = Object.fromEntries(
  COMPANY_DEPARTMENTS.map((dept) => [dept.slug, dept]),
) as Record<string, CompanyDepartment>

export const DEPARTMENT_BY_LABEL = Object.fromEntries(
  COMPANY_DEPARTMENTS.map((dept) => [dept.label, dept]),
) as Record<string, CompanyDepartment>

export function departmentLabelForSlug(slug: string): string {
  return DEPARTMENT_BY_SLUG[slug]?.label ?? slug
}
