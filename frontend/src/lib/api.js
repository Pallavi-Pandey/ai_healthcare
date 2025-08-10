const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function getApiBase() {
  return API_BASE
}

function getStoredAccessToken() {
  return localStorage.getItem('access_token') || null
}

function authHeaders() {
  const token = getStoredAccessToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`
  const baseHeaders = { 'Content-Type': 'application/json', ...authHeaders() }
  const headers = { ...baseHeaders, ...(options.headers || {}) }
  const res = await fetch(url, { ...options, headers })
  const contentType = res.headers.get('content-type') || ''
  let data = null
  if (contentType.includes('application/json')) {
    data = await res.json()
  } else {
    const text = await res.text()
    data = text ? { message: text } : null
  }
  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || `Request failed with ${res.status}`
    const err = new Error(msg)
    err.status = res.status
    err.data = data
    throw err
  }
  return data
}

// OpenAPI: LoginRequest requires { email, password, role }
// Response: Token { access_token, refresh_token, token_type }
export async function login({ email, password, role }) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password, role }),
  })
}

export function storeTokens(tokenObj) {
  if (!tokenObj) return
  if (tokenObj.access_token) localStorage.setItem('access_token', tokenObj.access_token)
  if (tokenObj.refresh_token) localStorage.setItem('refresh_token', tokenObj.refresh_token)
}

export async function refreshToken() {
  const refresh_token = localStorage.getItem('refresh_token')
  if (!refresh_token) throw new Error('No refresh token found')
  const data = await apiFetch('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token }),
  })
  storeTokens(data)
  return data
}

export async function me() {
  return apiFetch('/auth/me', { method: 'GET' })
}
