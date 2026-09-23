import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { Dashboard } from './pages/Dashboard'
import { Interview } from './pages/Interview'
import { ReportPage } from './pages/ReportPage'
import { CandidatePage } from './pages/CandidatePage'
import { Rubrics } from './pages/Rubrics'
import './styles.css'

export default function App() {
  return <BrowserRouter><AppShell><Routes><Route path="/" element={<Dashboard/>}/><Route path="/interview/:sessionId" element={<Interview/>}/><Route path="/report/:sessionId" element={<ReportPage/>}/><Route path="/candidate/:candidateId" element={<CandidatePage/>}/><Route path="/rubrics" element={<Rubrics/>}/></Routes></AppShell></BrowserRouter>
}
