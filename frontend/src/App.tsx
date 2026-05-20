import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthGuard } from './components/layout/AuthGuard'
import { DrivePage } from './pages/DrivePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <AuthGuard>
              <DrivePage />
            </AuthGuard>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
