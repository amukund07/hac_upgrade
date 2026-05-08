import axios from 'axios'
import { getAuthToken } from './authStorage'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken()

  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})