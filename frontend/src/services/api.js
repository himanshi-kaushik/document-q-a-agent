import axios from 'axios'

const apiClient = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    'http://127.0.0.1:8000',
  timeout: 120000,
})

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post(
    '/documents/upload',
    formData,
  )

  return response.data
}

export async function askQuestion({
  documentId,
  sessionId,
  question,
}) {
  const response = await apiClient.post(
    '/questions/ask',
    {
      document_id: documentId,
      session_id: sessionId,
      question,
    },
  )

  return response.data
}
