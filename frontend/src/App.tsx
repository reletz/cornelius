import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ConfigPage from './pages/ConfigPage'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import ClusteringPage from './pages/ClusteringPage'
import GenerationPage from './pages/GenerationPage'
import ReviewPage from './pages/ReviewPage'
import { useAppStore } from './store/appStore'

function App() {
  const { apiKey } = useAppStore()

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ConfigPage />} />
        <Route 
          path="/upload" 
          element={apiKey ? <UploadPage /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/processing" 
          element={apiKey ? <ProcessingPage /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/clustering" 
          element={apiKey ? <ClusteringPage /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/generation" 
          element={apiKey ? <GenerationPage /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/review" 
          element={apiKey ? <ReviewPage /> : <Navigate to="/" replace />} 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
