import { Routes, Route, Link } from 'react-router-dom'
import './App.css'
import Landing from './pages/Landing'
import Login from './pages/Login'

function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100">
      <header className="border-b border-slate-200/50 dark:border-slate-800 sticky top-0 bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <Link to="/" className="font-semibold text-lg tracking-tight">AI Healthcare</Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link className="hover:text-primary" to="/">Home</Link>
            <Link className="hover:text-primary" to="/login">Login</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
