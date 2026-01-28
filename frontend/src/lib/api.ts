import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add API key to requests that need it
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('cornell-notes-storage')
  if (apiKey) {
    try {
      const parsed = JSON.parse(apiKey)
      if (parsed.state?.apiKey) {
        config.headers['X-API-Key'] = parsed.state.apiKey
      }
    } catch {
      // Ignore parse errors
    }
  }
  return config
})

export default api

// ===== Config API =====
export const validateApiKey = async (apiKey: string) => {
  const response = await api.post('/config/validate-key', { api_key: apiKey })
  return response.data
}

// ===== Session API =====
export const createSession = async () => {
  const response = await api.post('/sessions/')
  return response.data
}

export const getSession = async (sessionId: string) => {
  const response = await api.get(`/sessions/${sessionId}`)
  return response.data
}

export const deleteSession = async (sessionId: string) => {
  const response = await api.delete(`/sessions/${sessionId}`)
  return response.data
}

// ===== Upload API =====
export const uploadFiles = async (sessionId: string, files: File[]) => {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  
  const response = await api.post(`/upload/?session_id=${sessionId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const listDocuments = async (sessionId: string) => {
  const response = await api.get(`/upload/${sessionId}`)
  return response.data
}

// ===== Cluster API =====
export const analyzeAndCluster = async (sessionId: string) => {
  const response = await api.post(`/clusters/analyze/${sessionId}`)
  return response.data
}

export const listClusters = async (sessionId: string) => {
  const response = await api.get(`/clusters/${sessionId}`)
  return response.data
}

export const updateCluster = async (clusterId: string, data: { title?: string; sources_json?: object }) => {
  const response = await api.patch(`/clusters/${clusterId}`, data)
  return response.data
}

export const deleteCluster = async (clusterId: string) => {
  const response = await api.delete(`/clusters/${clusterId}`)
  return response.data
}

export const mergeClusters = async (clusterIds: string[], newTitle: string) => {
  const response = await api.post('/clusters/merge', {
    cluster_ids: clusterIds,
    new_title: newTitle,
  })
  return response.data
}

// ===== Generation API =====
export const generateNotes = async (sessionId: string, clusterIds?: string[]) => {
  const response = await api.post('/generate/', {
    session_id: sessionId,
    cluster_ids: clusterIds,
  })
  return response.data
}

export const getGenerationStatus = async (taskId: string) => {
  const response = await api.get(`/generate/status/${taskId}`)
  return response.data
}

export const listNotes = async (sessionId: string) => {
  const response = await api.get(`/generate/notes/${sessionId}`)
  return response.data
}

export const getNote = async (noteId: string) => {
  const response = await api.get(`/generate/note/${noteId}`)
  return response.data
}

// ===== Export API =====
export const exportMarkdown = (sessionId: string) => {
  return `/api/export/${sessionId}/markdown`
}

export const exportPdf = (sessionId: string) => {
  return `/api/export/${sessionId}/pdf`
}

export const exportNotePdf = (noteId: string) => {
  return `/api/export/note/${noteId}/pdf`
}

// ===== GitHub API =====
export const validateGitHubConfig = async (pat: string, repo: string, path: string) => {
  const response = await api.post('/github/validate', { pat, repo, path })
  return response.data
}

export const syncToGitHub = async (
  sessionId: string, 
  config: { pat: string; repo: string; path: string },
  noteIds?: string[]
) => {
  const response = await api.post('/github/sync', {
    session_id: sessionId,
    note_ids: noteIds,
  }, {
    params: config,
  })
  return response.data
}
