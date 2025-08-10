import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, getApiBase, storeTokens } from '../lib/api'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('patient')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)
    try {
      const res = await login({ email, password, role })
      // OpenAPI Token: { access_token, refresh_token, token_type }
      if (res && (res.access_token || res.refresh_token)) {
        storeTokens(res)
        setMessage('Login successful! Redirecting...')
        setTimeout(() => navigate('/'), 800)
      } else {
        setError('Login succeeded but no token returned. Please verify API response.')
      }
    } catch (err) {
      const details = err?.data?.detail
      const msg = Array.isArray(details)
        ? details.map(d => d?.msg).filter(Boolean).join(', ')
        : (err?.message || 'Login failed')
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem', maxWidth: 420, margin: '0 auto' }}>
      <h2 style={{ marginBottom: '1rem' }}>Login</h2>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>API: {getApiBase()}/auth/login</p>

      <form onSubmit={onSubmit} style={{ display: 'grid', gap: '0.75rem' }}>
        <label style={{ display: 'grid', gap: '0.25rem' }}>
          <span style={{ fontSize: 14 }}>Role</span>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            required
            style={{ padding: '0.6rem 0.75rem', border: '1px solid #cbd5e1', borderRadius: 8 }}
          >
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        <label style={{ display: 'grid', gap: '0.25rem' }}>
          <span style={{ fontSize: 14 }}>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="you@example.com"
            style={{ padding: '0.6rem 0.75rem', border: '1px solid #cbd5e1', borderRadius: 8 }}
          />
        </label>

        <label style={{ display: 'grid', gap: '0.25rem' }}>
          <span style={{ fontSize: 14 }}>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            style={{ padding: '0.6rem 0.75rem', border: '1px solid #cbd5e1', borderRadius: 8 }}
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.75rem 1rem',
            background: loading ? '#94a3b8' : '#2563eb',
            color: 'white',
            borderRadius: 8,
            border: 'none',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginTop: '0.5rem',
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {error && <div style={{ color: '#dc2626' }}>{error}</div>}
        {message && <div style={{ color: '#16a34a' }}>{message}</div>}
      </form>
    </div>
  )
}
