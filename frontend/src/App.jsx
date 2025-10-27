import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import InterviewList from './pages/InterviewList'
import InterviewSession from './pages/InterviewSession'
import InterviewReport from './pages/InterviewReport'
import InterviewAssessment from './pages/InterviewAssessment'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function PrivateRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="interviews" element={<InterviewList />} />
        <Route path="interview/:id" element={<InterviewSession />} />
        <Route path="interview/:id/report" element={<InterviewReport />} />
        <Route path="interview/:id/assessment" element={<InterviewAssessment />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
