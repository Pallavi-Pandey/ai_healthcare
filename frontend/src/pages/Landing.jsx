import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem', maxWidth: 960, margin: '0 auto' }}>
      <section style={{ display: 'grid', gap: '1.25rem' }}>
        <p>
          Welcome to AI Healthcare – an AI-powered appointment scheduler and patient care hub.
          Manage appointments, doctors, prescriptions, reminders, and more.
        </p>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/login" style={{ padding: '0.75rem 1rem', background: '#2563eb', color: 'white', borderRadius: 8, textDecoration: 'none' }}>Get Started</Link>
          <a href="/docs" style={{ padding: '0.75rem 1rem', border: '1px solid #cbd5e1', borderRadius: 8, textDecoration: 'none' }}>API Docs</a>
        </div>
      </section>

      <section style={{ marginTop: '2rem' }}>
        <h2>Core Features</h2>
        <ul>
          <li>Authentication & User Management</li>
          <li>Doctor Management</li>
          <li>Appointment Scheduling & Availability</li>
          <li>Prescriptions & Medication Reminders</li>
          <li>AI Voice Call Integration</li>
          <li>Notifications & Messaging</li>
          <li>Analytics & Reports</li>
        </ul>
      </section>
    </div>
  )
}
