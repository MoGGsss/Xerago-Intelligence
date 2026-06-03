import { COMPANY_DEPARTMENTS } from '../constants/departments'

export const DEMO_PASSWORD = 'Xerago@123'

export interface DemoUser {
  email: string
  password: string
  department: string
}

function departmentEmail(slug: string): string {
  return `${slug}@xerago.demo`
}

export const DEMO_USERS: readonly DemoUser[] = COMPANY_DEPARTMENTS.map((dept) => ({
  email: departmentEmail(dept.slug),
  password: DEMO_PASSWORD,
  department: dept.label,
}))

const DEMO_USER_BY_EMAIL = Object.fromEntries(
  DEMO_USERS.map((user) => [user.email.toLowerCase(), user]),
) as Record<string, DemoUser>

export function findDemoUser(email: string, password: string): DemoUser | null {
  const user = DEMO_USER_BY_EMAIL[email.trim().toLowerCase()]
  if (!user || user.password !== password) {
    return null
  }
  return user
}

export function departmentForEmail(email: string): string | null {
  return DEMO_USER_BY_EMAIL[email.trim().toLowerCase()]?.department ?? null
}

export function isLoggedIn(): boolean {
  return Boolean(localStorage.getItem('userEmail') && localStorage.getItem('department'))
}

export function getLoggedInEmail(): string | null {
  return localStorage.getItem('userEmail')
}

export function getLoggedInDepartment(): string | null {
  return localStorage.getItem('department')
}

export function getLastLoginAt(): string | null {
  return localStorage.getItem('lastLoginAt')
}

export function saveLogin(user: DemoUser): void {
  localStorage.setItem('userEmail', user.email.toLowerCase())
  localStorage.setItem('department', user.department)
  localStorage.setItem('lastLoginAt', new Date().toISOString())
}

export function clearLogin(): void {
  localStorage.removeItem('userEmail')
  localStorage.removeItem('department')
  localStorage.removeItem('lastLoginAt')
}
