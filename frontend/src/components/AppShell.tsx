import { Link, useLocation } from 'react-router-dom'
import { BarChart3, ClipboardCheck, FileText, ShieldCheck, Sparkles } from 'lucide-react'
import type { ReactNode } from 'react'

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const nav = [
    { href: '/', label: 'Dashboard', icon: BarChart3 },
    { href: '/rubrics', label: 'Rubrics', icon: ShieldCheck },
  ]
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Sparkles size={18} /></div><div><strong>HireIQ</strong><span>Interview Intelligence</span></div></div>
        <nav>
          {nav.map(item => {
            const Icon = item.icon
            const active = location.pathname === item.href || (item.href !== '/' && location.pathname.startsWith(item.href))
            return <Link className={active ? 'nav-item active' : 'nav-item'} key={item.href} to={item.href}><Icon size={17} /> {item.label}</Link>
          })}
        </nav>
        <div className="sidebar-foot"><FileText size={16} /><span>Security-first MVP</span></div>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}
