export interface DemoUser {
  email: string
  password: string
  department: string
}

export const DEMO_USERS: readonly DemoUser[] = [
  { email: 'ai@xerago.demo', password: 'Xerago@123', department: 'AI Department' },
  {
    email: 'cloud@xerago.demo',
    password: 'Xerago@123',
    department: 'Cloud Department',
  },
  {
    email: 'marketing@xerago.demo',
    password: 'Xerago@123',
    department: 'Marketing Department',
  },
  {
    email: 'analytics@xerago.demo',
    password: 'Xerago@123',
    department: 'Analytics Department',
  },
  {
    email: 'leadership@xerago.demo',
    password: 'Xerago@123',
    department: 'Leadership Department',
  },
]

export function findDemoUser(email: string, password: string): DemoUser | null {
  const normalizedEmail = email.trim().toLowerCase()
  return (
    DEMO_USERS.find(
      (user) =>
        user.email.toLowerCase() === normalizedEmail && user.password === password.trim(),
    ) ?? null
  )
}

export function isLoggedIn(): boolean {
  return Boolean(localStorage.getItem('userEmail') && localStorage.getItem('department'))
}

export function saveLogin(user: DemoUser): void {
  localStorage.setItem('userEmail', user.email)
  localStorage.setItem('department', user.department)
  localStorage.setItem('lastLoginAt', new Date().toISOString())
}

export function clearLogin(): void {
  localStorage.removeItem('userEmail')
  localStorage.removeItem('department')
  localStorage.removeItem('lastLoginAt')
}
